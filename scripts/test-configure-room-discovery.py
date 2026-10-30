import importlib.util
import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('discovery',Path(__file__).with_name('configure-room-discovery.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class StableEndpointTests(unittest.TestCase):
    def test_lab_denial_uses_existing_alb_without_security_changes(self):
        calls=[]; configured=[]
        def aws(*args):
            calls.append(args)
            if args[:2]==('sts','get-caller-identity'):return {'Account':'055652951832'}
            if args[:2]==('ecs','describe-services'):return {'services':[{'serviceName':'room-service','networkConfiguration':{'awsvpcConfiguration':{'subnets':['subnet-test']}}},{'serviceName':'booking-service','taskDefinition':'old-task'}]}
            if args[:2]==('ec2','describe-subnets'):return {'Subnets':[{'VpcId':'vpc-test'}]}
            if args[:2]==('servicediscovery','list-namespaces'):return {'Namespaces':[]}
            if args[:2]==('servicediscovery','create-private-dns-namespace'):raise subprocess.CalledProcessError(254,args,stderr='AccessDeniedException')
            if args[:2]==('elbv2','describe-load-balancers'):return {'LoadBalancers':[{'DNSName':'existing-alb.test','State':{'Code':'active'}}]}
            self.fail(str(args))
        with patch.object(module,'aws',aws),patch.object(module,'configure_booking_endpoint',lambda *a:configured.append(a)):
            module.main()
        self.assertEqual(configured[0][-1],'http://existing-alb.test')
        self.assertFalse(any('security-group' in str(a) or a[0]=='iam' for a in calls))

    def test_task_update_preserves_secrets_and_other_containers(self):
        task={'family':'booking','revision':2,'networkMode':'awsvpc','executionRoleArn':'exec-role','taskRoleArn':'task-role','containerDefinitions':[{'name':'booking-service','image':'old-image','environment':[{'name':'OTHER','value':'keep'},{'name':'ROOM_SERVICE_URL','value':'http://old:8080'}],'secrets':[{'name':'SPRING_DATASOURCE_PASSWORD','valueFrom':'ssm-ref'}]},{'name':'sidecar','image':'keep-sidecar'}]}
        submitted=[]
        def aws(*args):
            if args[1]=='describe-task-definition':return {'taskDefinition':task}
            if args[1]=='register-task-definition':
                submitted.append(json.loads(Path(args[-1][7:]).read_text()));return {'taskDefinition':{'taskDefinitionArn':'new-task'}}
            return {}
        with patch.object(module,'aws',aws):module.configure_booking_endpoint('hotel-cluster',{'taskDefinition':'old-task'},'http://stable-alb')
        new=submitted[0]
        self.assertNotIn('revision',new)
        self.assertEqual(new['containerDefinitions'][0]['secrets'],[{'name':'SPRING_DATASOURCE_PASSWORD','valueFrom':'ssm-ref'}])
        self.assertEqual(new['containerDefinitions'][1]['image'],'keep-sidecar')
        self.assertEqual(new['containerDefinitions'][0]['image'],'old-image')
        self.assertEqual(new['taskRoleArn'],'task-role')
        self.assertIn({'name':'OTHER','value':'keep'},new['containerDefinitions'][0]['environment'])

    def test_waiter_empty_stdout_is_valid(self):
        with patch.object(module.subprocess,'run',return_value=subprocess.CompletedProcess([],0,stdout='',stderr='')):
            self.assertEqual(module.aws('ecs','wait','services-stable'),{})

if __name__=='__main__':unittest.main()
