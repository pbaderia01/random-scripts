import paramiko
import time
import datetime
import re
import threading
import math
import boto3
import json

class clients:
    def __init__(self,ip,private_key,username,output=""):
        self.ip = ip
        self.private_key = private_key
        self.username = username
        self.output=output

clients_to_connect = []
number_of_clients = input("Please enter the number of clients to connect to ")
asg = raw_input("Please enter the name of the asg to connect to ")
rsa_keys = []
ssh_clients = []
private_ip = []
instance_ids = []
private_ip = []
total_clients = 0

def get_ips():
    stsclient = boto3.client('sts')
    stsjsonresponse =stsclient.assume_role(
        RoleSessionName='Example',
        RoleArn='YOUR_ROLE_ARN',
        DurationSeconds= 3600
     )
    stsresponse = stsjsonresponse
    aws_access_key = stsresponse['Credentials']['AccessKeyId']
    aws_secret_access_key = stsresponse['Credentials']['SecretAccessKey']
    session_token = stsresponse['Credentials']['SessionToken']
    asg_client = boto3.client('autoscaling',aws_access_key_id=aws_access_key,aws_secret_access_key=aws_secret_access_key,aws_session_token=session_token,region_name='YOUR_REGION')
    asg_response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg])
    instance_ids = [] # List to hold the instance-ids
    for i in asg_response['AutoScalingGroups']:
        for k in i['Instances']:
            instance_ids.append(k['InstanceId'])
    global total_clients
    total_clients = len(instance_ids)
    ec2_client = boto3.client('ec2',aws_access_key_id=aws_access_key,aws_secret_access_key=aws_secret_access_key,aws_session_token=session_token,region_name='ap-south-1')
    ec2_response = ec2_client.describe_instances(
            InstanceIds = instance_ids
            )
    for instances in ec2_response['Reservations']:
        for ip in instances['Instances']:
            private_ip.append(ip['PrivateIpAddress'])
    print ("\n").join(private_ip)


def get_hosts(i):
    global clients_to_connect
    clients_to_connect = []
    for j in range(number_of_clients):
        if private_ip[j+number_of_clients*i] is not None:
            ip_client = private_ip[j+number_of_clients*i]
        else:
            break
        private_key_client = "YOUR PATH TO YOUR PRIVATE KEY"
        username_client = "YOUR USERNAME TO BE USED FOR SSH"
        clients_to_connect.append(clients(ip_client,private_key_client,username_client))
    k = 0
    global rsa_keys
    rsa_keys = []
    global ssh_clients
    ssh_clients = []
    for k in range(len(clients_to_connect)):
        rsa_keys.append(paramiko.RSAKey.from_private_key_file(clients_to_connect[k].private_key))
        ssh_clients.append(paramiko.SSHClient())
    return len(clients_to_connect)

def ssh_execute(i,command):
    stdin , stdout , stderr = ssh_clients[i].exec_command(command)
    clients_to_connect[i].output = stdout.read()

def ssh_output(i):
    print("Host {}:  {}".format(i, clients_to_connect[i].output))

def ssh_close(i):
    print("Client {} connection closed.".format(i))
    ssh_clients[i].close()

def ssh_connect(i):
    global ssh_clients
    print("Connecting to Host {}".format(i))
    ssh_clients[i].set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_clients[i].connect(hostname = clients_to_connect[i].ip, username = clients_to_connect[i].username, pkey = rsa_keys[i])
    print("Connected to Host {}".format(i))
    ssh_exec()

def ssh_exec():
    i=0
    thread_instance = []
    toggle = raw_input("Do you want to imput a command, please input y or n:")
    while(toggle == 'y'):
        command = raw_input("Please enter command ")
        print "Executing {}".format(command)
        for i in range(number_of_clients):
            thread = threading.Thread(target=ssh_execute,args=(i,command,))
            thread.start()
            thread_instance.append(thread)

        for thr in thread_instance:
            thr.join()

        for i in range(number_of_clients):
            ssh_output(i)
        toggle = raw_input("Do you want to imput a command, please input y or n: ")

    if(toggle == 'n'):
        for i in range(number_of_clients):
            ssh_close(i)

def ssh_thread():
    get_ips()
    rangeOfExec = int(math.ceil(total_clients/number_of_clients))
    for i in range(rangeOfExec):
        clients_to_connect = get_hosts(i)
        for j in range(clients_to_connect):
            ssh_connect(j)

if __name__ == '__main__':
    ssh_thread()
                                                                