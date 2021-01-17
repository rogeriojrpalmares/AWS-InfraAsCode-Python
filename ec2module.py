import boto3
import sys

ec2 = boto3.resource('ec2')
client = boto3.client('ec2')

def describe_vpc ():
    print('Available VPCs: ')
    for vpcid in client.describe_vpcs()['Vpcs']:
        print (vpcid['VpcId'])
        for i in vpcid['Tags']:
            print('VPC Name: ', i['Value'])

def describe_sg (vpc):

    print('Available Security Groups: ')
    for sgid in client.describe_security_groups()['SecurityGroups']:
        if sgid['VpcId'] == vpc:
            print(sgid['GroupId'] + " - Name: " + sgid['GroupName'] + " - VPC ID: " + sgid['VpcId'])

def describe_subnets (vpc):
    print('Available Subnets: \n')
    for subnets in client.describe_subnets()['Subnets']:
        if vpc == subnets['VpcId']:
            print(subnets['SubnetId'] + ', CIDR: ' + subnets['CidrBlock'] + ' ,VPC: ' + subnets['VpcId'] + ', Availability Zone: ' + subnets['AvailabilityZoneId'])
            for i in subnets['Tags']:
                print('Subnet Name: ', i['Value'])

def create_instance(ami,
                    subnet,
                    name):
    try:
        print("Creating EC2 instance...")
        instance = ec2.create_instances(

            ImageId=ami,
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
                    'SubnetId': subnet,
                }
            ],
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value':  name
                        },
                    ]
                },
            ]
        )
        #Waits the instance to be available
        waiter1 = client.get_waiter('instance_running')
        waiter1.wait(
            InstanceIds=[
                instance[0].id
            ]
        )

    except Exception as e:

        print(e)
        sys.exit(1)

    else:
        print("EC2 instance {} is now available!".format(instance[0].id))
        return instance[0].id


def create_second_int(sg, priv_sub):
    try:
        print("Creating the second network interface")
        secondary_interface = client.create_network_interface(
            Groups=[
                sg
            ],
            SubnetId=priv_sub
        )

    except Exception:
        print("An error occurred, when creating the interface!")
        sys.exit(1)

    else:
        return secondary_interface['NetworkInterface']['NetworkInterfaceId']

def attach_interface(instanceid, interfaceid):
    try:
        interface_attach = client.attach_network_interface(
            DeviceIndex=1,
            InstanceId=instanceid,
            NetworkInterfaceId=interfaceid
        )
    except Exception:

        print("Error occurred when you tried to attach the interface, closing the program")
        sys.exit(1)

    else:
        print("Secondary interface {} was attached".format(interfaceid))

#Describing Instance to get its interface ID


def primary_interface (instanceid):

    try:
        describe = client.describe_instances(
            InstanceIds=[
                instanceid
            ],

        )
    except Exception:

        print("Error describing EC2")
        sys.exit(1)

    else:
        return describe['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['NetworkInterfaceId']


def associate_elasticip(interfaceid):

    try:
        print("Associating Elastic IP...")
        client.associate_address(
            AllocationId='eipalloc-00db592eef054d7b6',
            AllowReassociation=True,
            NetworkInterfaceId=interfaceid
        )
    except Exception:

        print("An error occurred when you tried to associate the Elastic IP")

    else:
        print("Elastic IP associated with interface {}".format(interfaceid))


def create_vgw ():
    try:
        vpn_gateway = client.create_vpn_gateway(
            Type='ipsec.1',
        )

    except Exception as e:
        print(e)
        sys.exit(1)

    else:
        print("Virtual Private Gateway {} created successfully".format(vpn_gateway['VpnGateway']['VpnGatewayId']))
        return vpn_gateway['VpnGateway']['VpnGatewayId']


def attach_vgw(gateway_id, vpc):
    try:
        client.attach_vpn_gateway(
            VpcId=vpc,
            VpnGatewayId=gateway_id,
        )
    except Exception as e:

        print(e)
        sys.exit(1)
    else:
        print ('VGW {} attached to the VPC {}'.format(gateway_id, vpc))


def create_cgw(publicip='176.34.145.12'):

    try:
        print("Creating the Customer Gateway")
        cgw = client.create_customer_gateway(
            BgpAsn=65000,
            PublicIp=publicip,
            Type='ipsec.1',
            DeviceName='StrongSwanVPN',
        )
    except Exception as e:

        print(e)

    else:
        print("Customer gateway {} created succesfully".format(cgw['CustomerGateway']['CustomerGatewayId']))

        return cgw['CustomerGateway']['CustomerGatewayId']


def create_s2s(cgw_id, vgw_id):
    try:
        s2s_conn = client.create_vpn_connection(
            CustomerGatewayId=cgw_id,
            Type='ipsec.1',
            VpnGatewayId=vgw_id,
            Options={
                'EnableAcceleration': False,
                'StaticRoutesOnly': False,
                'TunnelInsideIpVersion': 'ipv4',
            },
            TagSpecifications=[
                {
                    'ResourceType': 'vpn-connection',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'S2SStrongSwan'
                        },
                    ]
                },
            ]
        )
    except Exception as e:
        print(e)
    else:
        print("Site to site connection " + s2s_conn['VpnConnection']['VpnConnectionId'] + ' created successfully')

