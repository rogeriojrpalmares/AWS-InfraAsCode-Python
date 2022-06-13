import boto3
import botocore
import time


def lambda_handler(event=None, context=None):
    client = boto3.client('ssm')

    instance_id = event['detail']['instance-id']
    
    response_1 = client.describe_instance_information(
        
        Filters=[
            {
                'Key': 'InstanceIds',
                'Values': [
                    instance_id,
                ]
            },
        ]
        
        )['InstanceInformationList'][0]['PlatformType']
    
    print (response_1)
    
    if response_1 != "Windows":
    
        client.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={
                'commands': [
                    # Simple test if a file exists
                    'echo " Public IP: $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)" ',
                    'echo "EC2 ID: $(curl -s curl http://169.254.169.254/latest/meta-data/instance-id)" ',
                    'echo " Platform: Linux"'
                ]
            },
            CloudWatchOutputConfig={
            'CloudWatchLogGroupName': 'publicip-tracking',
            'CloudWatchOutputEnabled': True
        }
        )
        
    else:
        
        client.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunPowerShellScript',
            Parameters={
                'commands': [
                    # Simple test if a file exists
                    'echo " Public IP: $(curl.exe -s http://169.254.169.254/latest/meta-data/public-ipv4)" ',
                    'echo " Instance ID: $(curl.exe -s http://169.254.169.254/latest/meta-data/instance-id)" ',
                    'echo " Platform: Windows"'
                ]
            },
            CloudWatchOutputConfig={
            'CloudWatchLogGroupName': 'publicip-tracking',
            'CloudWatchOutputEnabled': True
        }
        )
