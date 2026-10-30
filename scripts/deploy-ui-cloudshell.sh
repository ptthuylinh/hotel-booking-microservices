#!/usr/bin/env bash
# Run from the repository root inside AWS CloudShell. Never changes RDS data or security groups.
set -euo pipefail
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-east-1}"
export AWS_PAGER=""
CLUSTER="${CLUSTER:-hotel-cluster}"
ALB_NAME="${ALB_NAME:-hotel-booking-alb}"
EXPECTED_ACCOUNT="${EXPECTED_ACCOUNT:-055652951832}"
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
[[ "$ACCOUNT" == "$EXPECTED_ACCOUNT" ]] || { echo "Wrong AWS account: $ACCOUNT"; exit 1; }
[[ -z "$(git status --porcelain)" ]] || { echo 'Checkout must be clean before deployment.'; exit 1; }
TAG="ui-$(git rev-parse --short=12 HEAD)"
REGISTRY="$ACCOUNT.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"
TASK_DIR=$(mktemp -d)
trap 'rm -rf "$TASK_DIR"' EXIT
export DOCKER_CONFIG="$TASK_DIR/docker"
mkdir -p "$DOCKER_CONFIG"
aws ecs describe-services --cluster "$CLUSTER" --services room-service booking-service notification-service > "$TASK_DIR/services.json"
python3 - "$TASK_DIR/services.json" <<'PY'
import json,sys
v=json.load(open(sys.argv[1]))
assert not v.get('failures'),v.get('failures')
assert len(v['services'])==3,'Missing existing ECS services'
assert all(s['status']=='ACTIVE' for s in v['services']),'Inactive ECS service'
print('Deploying existing services:',', '.join(s['serviceName'] for s in v['services']))
PY
# Start the existing database only if stopped; preserve instance, schema and data.
DB_STATUS=$(aws rds describe-db-instances --db-instance-identifier hotel-db-instance --query 'DBInstances[0].DBInstanceStatus' --output text)
if [[ "$DB_STATUS" == stopped ]]; then
  aws rds start-db-instance --db-instance-identifier hotel-db-instance --query 'DBInstance.DBInstanceStatus' --output text
elif [[ "$DB_STATUS" != available && "$DB_STATUS" != starting ]]; then
  echo "Database state $DB_STATUS requires attention."; exit 1
fi
aws ecr get-login-password | docker login --username AWS --password-stdin "$REGISTRY"
for SERVICE in room-service booking-service notification-service; do
  REPO="hotel-$SERVICE"
  aws ecr describe-repositories --repository-names "$REPO" --query 'repositories[0].repositoryName' --output text
  docker build -t "$REGISTRY/$REPO:$TAG" "$SERVICE"
  docker push "$REGISTRY/$REPO:$TAG"
done
aws rds wait db-instance-available --db-instance-identifier hotel-db-instance
# Clone each service's active task definition, changing only its application image.
python3 - "$TASK_DIR" "$REGISTRY" "$TAG" "$CLUSTER" <<'PY'
import json,subprocess,sys,pathlib
folder,registry,tag,cluster=sys.argv[1:]
def aws(*args): return json.loads(subprocess.check_output(['aws',*args,'--output','json']))
services=json.load(open(folder+'/services.json'))['services']
rollback=[]
for service in services:
    name=service['serviceName']; old=service['taskDefinition']
    task=aws('ecs','describe-task-definition','--task-definition',old)['taskDefinition']
    allowed={'family','taskRoleArn','executionRoleArn','networkMode','containerDefinitions','volumes','placementConstraints','requiresCompatibilities','cpu','memory','pidMode','ipcMode','proxyConfiguration','inferenceAccelerators','ephemeralStorage','runtimePlatform','enableFaultInjection'}
    task={k:v for k,v in task.items() if k in allowed}
    candidates=[c for c in task['containerDefinitions'] if c['name']==name or c['image'].split('/')[-1].split(':')[0]=='hotel-'+name]
    assert len(candidates)==1, f'Cannot unambiguously identify container for {name}'
    candidates[0]['image']=f'{registry}/hotel-{name}:{tag}'
    path=pathlib.Path(folder)/f'{name}.json';path.write_text(json.dumps(task));path.chmod(0o600)
    new=aws('ecs','register-task-definition','--cli-input-json','file://'+str(path))['taskDefinition']['taskDefinitionArn']
    desired=max(1,service['desiredCount'])
    aws('ecs','update-service','--cluster',cluster,'--service',name,'--task-definition',new,'--desired-count',str(desired))
    rollback.append({'service':name,'previousTaskDefinition':old,'previousDesiredCount':service['desiredCount'],'newTaskDefinition':new})
    print(name,'->',new,flush=True)
pathlib.Path('deployment-rollback.json').write_text(json.dumps(rollback,indent=2))
PY
# Add a dedicated UI route; preserve all existing API listener rules and target groups.
python3 - "$ALB_NAME" "$TASK_DIR/services.json" <<'PY'
import json,subprocess,sys
def aws(*args):return json.loads(subprocess.check_output(['aws',*args,'--output','json']))
alb=aws('elbv2','describe-load-balancers','--names',sys.argv[1])['LoadBalancers'][0]
services=json.load(open(sys.argv[2]))['services']
room=next(s for s in services if s['serviceName']=='room-service')
assert len(room['loadBalancers'])==1,'Unexpected room target group configuration'
target=room['loadBalancers'][0]['targetGroupArn']
for listener in aws('elbv2','describe-listeners','--load-balancer-arn',alb['LoadBalancerArn'])['Listeners']:
    if listener['Protocol'] not in ('HTTP','HTTPS'):continue
    rules=aws('elbv2','describe-rules','--listener-arn',listener['ListenerArn'])['Rules']
    paths=['/','/ui','/ui/*']
    existing=next((r for r in rules if any(c.get('Field')=='path-pattern' and set(c.get('Values',c.get('PathPatternConfig',{}).get('Values',[])))==set(paths) for c in r['Conditions'])),None)
    actions=[{'Type':'forward','TargetGroupArn':target}]
    if existing:
        aws('elbv2','modify-rule','--rule-arn',existing['RuleArn'],'--actions',json.dumps(actions))
    else:
        priorities={int(r['Priority']) for r in rules if r['Priority']!='default'}
        priority=next(p for p in range(1,50000) if p not in priorities)
        aws('elbv2','create-rule','--listener-arn',listener['ListenerArn'],'--priority',str(priority),'--conditions',json.dumps([{'Field':'path-pattern','Values':paths}]),'--actions',json.dumps(actions))
print('UI_URL=http://'+alb['DNSName']+'/ui/index.html')
PY
aws ecs wait services-stable --cluster "$CLUSTER" --services room-service booking-service notification-service
aws ecs describe-services --cluster "$CLUSTER" --services room-service booking-service notification-service --query 'services[].[serviceName,desiredCount,runningCount,taskDefinition]' --output table
printf 'Deployment complete. Verify UI and APIs through ALB. Rollback ARNs: deployment-rollback.json\n'
