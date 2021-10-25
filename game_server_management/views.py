import random

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
import boto3


# Create your views here.
from game_server_management.models import Server


@login_required
def home(request):
    ec2 = boto3.client('ec2', region_name='us-west-2')
    response = ec2.describe_instances()
    # Lot of assumptions in the code below; only one instance, only on tag...
    # Should be able to update this to use an actual list of servers, and
    # to filter the results from AWS using filters in the 'describe_instances' function call.

    # Optionally, can use the ec2 instance object to grab each instance by id,
    # Which could be pulled from the db:
    # ec2 = boto3.resource('ec2')
    # instance = ec2.Instance('id')

    instanceName = response['Reservations'][0]['Instances'][0]['Tags'][0]['Value']

    return render(request, 'game_server_management/index.html', {'instanceName': instanceName})


@login_required
def create_new_server(request):

    # Create new instance:

    ec2 = boto3.client('ec2', region_name='us-west-2')
    response = ec2.run_instances(
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/sda1',
                'Ebs': {

                    'DeleteOnTermination': True,
                    'VolumeSize': 8,
                    'VolumeType': 'gp2'
                },
            },
        ],
        # Ubuntu 20.04 Image
        ImageId='ami-03d5c68bab01f3496',
        InstanceType='t2.micro',
        InstanceInitiatedShutdownBehavior='stop',
        # Could have this generated? Keep them all under one key for ease of testing.
        KeyName='game_server_key',
        MaxCount=1,
        MinCount=1,
        Monitoring={
            'Enabled': False
        },
        SecurityGroupIds=[
            # GameServerSecurityGroup
            'sg-075dc7cd3b70e4f12',
        ],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        # Users probably want to use their own name here:
                        'Value': 'MinecraftServer_' + str(request.user.id) + str(random.randint(1, 100))
                    }
                ]
            }
        ],
    )

    # Save new server object to DB, tied to the current user:

    new_server = Server()
    new_server.owner = request.user
    new_server.instance_id = response['Instances'][0]['InstanceId']
    new_server.save()

    # Redirect to homepage

    return redirect('home')
