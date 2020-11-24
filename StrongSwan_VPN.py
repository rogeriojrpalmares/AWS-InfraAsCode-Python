import boto3

ec2 = boto3.resource('ec2')
client = boto3.client('ec2')

#Creating new EC2 instance

instance = ec2.create_instances(

    ImageId='ami-0a4fba9176118e5a9',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro',
    KeyName='my-key',
    NetworkInterfaces=[
        {
            'DeleteOnTermination': True,
            'DeviceIndex': 0,
            'PrivateIpAddresses': [
                {
                    'Primary': True,

                },
            ],
            'SubnetId': 'subnet-0bb26a7bf0e04bbfe',
        }
    ],
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'name',
                    'Value': 'StronSwan+BGP'
                },
            ]
        },
    ]
)

waiter1 = client.get_waiter('instance_running')
waiter1.wait(
    InstanceIds=[
        instance[0].id
    ]
)

#Creating second network interface

secondary_interface = client.create_network_interface(
    Description='Client Interface',
    Groups=[
        'sg-039633e9f88c85cc0',
    ],
    SubnetId='subnet-02ba323e080af18f3'
)

Secondary_interface_ID = secondary_interface['NetworkInterface']['NetworkInterfaceId']

print('The Secondary Interface ID ' + Secondary_interface_ID + 'was created')

#Describing Instance to get its interface ID
describe = client.describe_instances(

    InstanceIds=[
        instance[0].id
    ],

)

Interface_ID = describe['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['NetworkInterfaceId']

#Attaching to the instance

print ("Attaching the secondary Interface...")

interface_attach = client.attach_network_interface(
    DeviceIndex=1,
    InstanceId=instance[0].id,
    NetworkInterfaceId=Secondary_interface_ID
)
print("Secondary interface {} was attached".format(Secondary_interface_ID))

print ("Associating Elastic IP...")
client.associate_address(
    AllocationId='eipalloc-00db592eef054d7b6',
    AllowReassociation=True,
    NetworkInterfaceId=Interface_ID
)

print ("Elastic IP associated with interface {}".format(Interface_ID))

#Creating VGW
print ("Creating Virtual Private Gateway...")
vpn_gateway = client.create_vpn_gateway(
        Type='ipsec.1',
    )
gateway_id = vpn_gateway['VpnGateway']['VpnGatewayId']

#Attaching VGW to VPC

print("Attaching the Virtual Private Gateway...")

try:
    client.attach_vpn_gateway(
        VpcId='vpc-0d68dc2c2d1db7cf0',
        VpnGatewayId=gateway_id,
    )
except:
    print('Ops, seems like the VpcId is already attached to other Virtual Private Gateway ')

#Creating CGW

print ("Creating the Customer Gateway")
cgw = client.create_customer_gateway(
    BgpAsn=65000,
    PublicIp='176.34.145.12',
    Type='ipsec.1',
    DeviceName='StrongSwanVPN',
)
cgw_id = cgw['CustomerGateway']['CustomerGatewayId']

#Creating Site to Site connection
try:
    s2s_conn = client.create_vpn_connection(
        CustomerGatewayId=cgw_id,
        Type='ipsec.1',
        VpnGatewayId=gateway_id,
        Options={
            'EnableAcceleration': False,
            'StaticRoutesOnly': False,
            'TunnelInsideIpVersion': 'ipv4',
            'TunnelOptions': [
                {
                    'PreSharedKey': 'labpassword'
                }
            ],
        },
        TagSpecifications=[
            {
                'ResourceType': 'vpn-connection',
                'Tags': [
                    {
                        'Key': 'name',
                        'Value': 'S2SStrongSwan'
                    },
                ]
            },
        ]
    )
except Exception as e:
    print(e)
else:
    print("Program was finished correctly")
