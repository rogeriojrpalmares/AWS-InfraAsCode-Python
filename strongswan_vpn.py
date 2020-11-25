import boto3
import ec2module

ec2 = boto3.resource('ec2')
client = boto3.client('ec2')

#Asking EC2 instance parameters
availableami = {'CSR 1000v': 'ami-0e47648335f79ea58', 'StrongSwan + FRRouting': 'ami-0a4fba9176118e5a9'}

print('Please provide the Subnet ID, for example subnet-0bb26a7bf0e04bbfe :')
subnet = input()

print('Please provide the AMI ID: ')
print("Those are the possible AMIs: ")
for key, value in availableami.items():
    print(' {}: {}'.format(key, value), end="")

ami = input()

print('Please provide a name: ')
name = input()

#Creating EC2 instance and saving the instance ID

instanceid = ec2module.create_instance(ami, subnet, name)

#Finding out the primary interface
primary_interface = ec2module.primary_interface(instanceid)
print(primary_interface)

#Creating second network interface

secondary_interface = ec2module.create_second_int()

#Attaching secondary interface to the instance

ec2module.attach_interface(instanceid, secondary_interface)

#Associating Elastic IP with the primary interface

ec2module.associate_elasticip(primary_interface)

#Creating VGW and storing its ID

vgw_id = ec2module.create_vgw()

#Attaching VGW to VPC

ec2module.attach_vgw(vgw_id)

#Creating CGW and storing CGW

cgw_id = ec2module.create_cgw()

#Creating Site to Site connection

ec2module.create_s2s(cgw_id, vgw_id)
