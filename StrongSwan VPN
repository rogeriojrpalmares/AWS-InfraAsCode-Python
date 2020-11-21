import boto3

ec2 = boto3.resource('ec2')

#Creating new EC2 instance

instance = ec2.create_instances(

    ImageId='ami-0a4fba9176118e5a9',
    MinCount=1,
    MaxCount=2,
    InstanceType='t2.micro',
    KeyName='my-key'

)
