import boto3
import ec2module

ec2 = boto3.resource('ec2')
client = boto3.client('ec2')

print("The default region used is eu-west-1 (DUB), please alter the document ~/.aws/config to change the region! \n")
#Describes all VPCs

ec2module.describe_vpc()
vpc = input('Type the VPC ID, please: ')

#Describes all Subnets Ids

ec2module.describe_subnets(vpc)

#Ask user for subnet-id:

print('Please provide a Public Subnet, followed by a Private Subnet in the same AZ and VPC: ')
pub_sub = input("Public Subnet: ")
priv_sub = input("Private Subnet: ")
#Asking EC2 instance parameters

availableami = {'CSR 1000v': 'ami-0e47648335f79ea58', 'StrongSwan + FRRouting': 'ami-0a4fba9176118e5a9'}

print("Current Available AMIs for VPN: ")

for key, value in availableami.items():
    print(' {}: {}'.format(key, value), end="")

print(' Please provide the AMI ID for your VPN: ')
ami = input()

print('Please provide a name: ')
name = input()

#Creating EC2 instance and saving the instance ID

instanceid = ec2module.create_instance(ami, pub_sub, name)

#Finding out the primary interface

primary_interface = ec2module.primary_interface(instanceid)
print('The primary interface is', primary_interface)

#Describing Security Groups

ec2module.describe_sg(vpc)
security_group = input("Choose a Security Group for the secondary interface: ")

#Creating second network interface

secondary_interface = ec2module.create_second_int(security_group, priv_sub)

print('Secondary interface was created', secondary_interface)

#Attaching secondary interface to the instance

ec2module.attach_interface(instanceid, secondary_interface)

#Associating Elastic IP with the primary interface

ec2module.associate_elasticip(primary_interface)

#Creating VGW and storing its ID

vgw_id = ec2module.create_vgw()

#Attaching VGW to VPC

ec2module.attach_vgw(vgw_id,vpc)

#Creating CGW and storing CGW

cgw_id = ec2module.create_cgw()

#Creating Site to Site connection

ec2module.create_s2s(cgw_id, vgw_id)
