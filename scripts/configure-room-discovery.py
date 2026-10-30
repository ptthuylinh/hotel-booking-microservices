#!/usr/bin/env python3
"""Configure stable room-service routing across ECS deployments and self-healing.
Run in authenticated AWS CloudShell after deploy-ui-cloudshell.sh succeeds.
Uses existing ALB when Cloud Map creation is denied by Lab policy.
Preserves the old hotel.local hosted zone and all Security Groups / RDS data.
"""
import json
import subprocess
import tempfile
import time
from pathlib import Path


def aws(*args):
    result = subprocess.run(['aws', *args, '--output', 'json'], capture_output=True, text=True, check=True)
    output = result.stdout
    return json.loads(output) if output.strip() else {}


def configure_booking_endpoint(cluster, booking, desired):
    task = aws('ecs', 'describe-task-definition', '--task-definition', booking['taskDefinition'])['taskDefinition']
    allowed = {'family', 'taskRoleArn', 'executionRoleArn', 'networkMode', 'containerDefinitions', 'volumes',
               'placementConstraints', 'requiresCompatibilities', 'cpu', 'memory', 'pidMode', 'ipcMode',
               'proxyConfiguration', 'inferenceAccelerators', 'ephemeralStorage', 'runtimePlatform', 'enableFaultInjection'}
    task = {k: v for k, v in task.items() if k in allowed}
    container = next(c for c in task['containerDefinitions'] if c['name'] == 'booking-service')
    env = container.setdefault('environment', [])
    old = next((e for e in env if e['name'] == 'ROOM_SERVICE_URL'), None)
    if old is None or old['value'] != desired:
        if old:
            old['value'] = desired
        else:
            env.append({'name': 'ROOM_SERVICE_URL', 'value': desired})
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'booking-task.json'
            path.write_text(json.dumps(task)); path.chmod(0o600)
            new = aws('ecs', 'register-task-definition', '--cli-input-json', 'file://' + str(path))['taskDefinition']['taskDefinitionArn']
        aws('ecs', 'update-service', '--cluster', cluster, '--service', 'booking-service', '--task-definition', new)
        print('Previous booking task:', booking['taskDefinition'])
        print('New booking task:', new)
    aws('ecs', 'wait', 'services-stable', '--cluster', cluster, '--services', 'booking-service')
    print('ROOM_ENDPOINT_READY=' + desired)


def main():
    account = aws('sts', 'get-caller-identity')['Account']
    if account != '055652951832':
        raise SystemExit('Wrong AWS account')
    cluster = 'hotel-cluster'
    services = aws('ecs', 'describe-services', '--cluster', cluster, '--services', 'room-service', 'booking-service')
    if services.get('failures'):
        raise SystemExit(str(services['failures']))
    room = next(s for s in services['services'] if s['serviceName'] == 'room-service')
    booking = next(s for s in services['services'] if s['serviceName'] == 'booking-service')
    subnet = room['networkConfiguration']['awsvpcConfiguration']['subnets'][0]
    vpc = aws('ec2', 'describe-subnets', '--subnet-ids', subnet)['Subnets'][0]['VpcId']
    namespace_name = 'hotel.internal'
    namespaces = aws('servicediscovery', 'list-namespaces')['Namespaces']
    namespace = next((n for n in namespaces if n['Name'] == namespace_name), None)
    if namespace is None:
        try:
            operation = aws('servicediscovery', 'create-private-dns-namespace', '--name', namespace_name,
                            '--vpc', vpc, '--description', 'Hotel ECS private service discovery')['OperationId']
        except subprocess.CalledProcessError as error:
            if 'AccessDenied' not in (error.stderr or ''):
                raise
            print('Cloud Map is not permitted in this Lab; using the existing ALB for stable REST routing.', flush=True)
            alb = aws('elbv2', 'describe-load-balancers', '--names', 'hotel-booking-alb')['LoadBalancers'][0]
            if alb['State']['Code'] != 'active':
                raise SystemExit('Existing ALB is not active; no endpoint changed.')
            configure_booking_endpoint(cluster, booking, 'http://' + alb['DNSName'])
            return
        for _ in range(120):
            result = aws('servicediscovery', 'get-operation', '--operation-id', operation)['Operation']
            if result['Status'] == 'SUCCESS':
                namespace = {'Id': result['Targets']['NAMESPACE']}
                break
            if result['Status'] == 'FAIL':
                raise SystemExit('Namespace failed: ' + result.get('ErrorMessage', 'unknown'))
            time.sleep(5)
        else:
            raise SystemExit('Namespace creation timed out; inspect Cloud Map before retrying.')
    namespace = aws('servicediscovery', 'get-namespace', '--id', namespace['Id'])['Namespace']
    hosted_zone = namespace['Properties']['DnsProperties']['HostedZoneId']
    associations = aws('route53', 'get-hosted-zone', '--id', hosted_zone)['VPCs']
    if vpc not in {v['VPCId'] for v in associations}:
        raise SystemExit('Existing namespace belongs to another VPC')
    existing = aws('servicediscovery', 'list-services', '--filters',
                   json.dumps([{'Name': 'NAMESPACE_ID', 'Values': [namespace['Id']], 'Condition': 'EQ'}]))['Services']
    discovery = next((s for s in existing if s['Name'] == 'room-service'), None)
    if discovery is None:
        discovery = aws('servicediscovery', 'create-service', '--name', 'room-service', '--dns-config',
                        json.dumps({'NamespaceId': namespace['Id'], 'RoutingPolicy': 'MULTIVALUE',
                                    'DnsRecords': [{'Type': 'A', 'TTL': 10}]}),
                        '--health-check-custom-config', '{"FailureThreshold":1}')['Service']
    registry = discovery['Arn']
    current = room.get('serviceRegistries', [])
    if current and current[0]['registryArn'] != registry:
        raise SystemExit('Unexpected existing service registry; inspect before changing.')
    if not current:
        aws('ecs', 'update-service', '--cluster', cluster, '--service', 'room-service',
            '--service-registries', json.dumps([{'registryArn': registry}]), '--force-new-deployment')
    aws('ecs', 'wait', 'services-stable', '--cluster', cluster, '--services', 'room-service')
    instances = aws('servicediscovery', 'list-instances', '--service-id', discovery['Id'])['Instances']
    if not instances:
        raise SystemExit('No room task registered in Cloud Map; booking was not changed.')
    configure_booking_endpoint(cluster, booking, 'http://room-service.hotel.internal:8080')
    print('ROOM_DISCOVERY_READY=' + desired)
    print('Cloud Map service:', registry)


if __name__ == '__main__':
    main()
