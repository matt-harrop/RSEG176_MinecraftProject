import random
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.shortcuts import render, redirect
import boto3

# Create your views here.
from game_server_management.forms import ScheduleCreationForm
from game_server_management.models import Server, Schedule


@login_required
def home(request):
    instance_ids_to_lookup = []
    server_objects = Server.objects.filter(owner=request.user)

    for server_object in server_objects:
        instance_ids_to_lookup.append(server_object.instance_id)

    ec2_resource = boto3.resource('ec2', region_name='us-west-2')

    if instance_ids_to_lookup:
        ec2_instances = ec2_resource.instances.filter(
            InstanceIds=instance_ids_to_lookup
        )
    else:
        ec2_instances = None

    full_instances = []
    for server_object in server_objects:
        dict_to_add = {"model_object": server_object}
        for aws_object in ec2_instances:
            if aws_object.instance_id == server_object.instance_id:
                dict_to_add["aws_object"] = aws_object
        full_instances.append(dict_to_add)

    return render(request, 'game_server_management/index.html', {
        # 'instances': ec2_instances,
        # 'server_objects': server_objects
        'instances': full_instances,
        'filler_price': server_objects[0].get_max_monthly_cost() if server_objects else "0.00"
    })


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
        # Custom Minecraft server AMI.
        ImageId='ami-021710cc2ad32742b',
        # Shouldn't need an image this large; just needed something with more memory than t2.micro for testing.
        InstanceType='t2.medium',
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

    # Any processing that needs to be done to new Server objects:
    new_server.billing_hours_month = datetime.now().month

    new_server.owner = request.user
    new_server.instance_id = response['Instances'][0]['InstanceId']
    new_server.save()

    # Redirect to homepage

    return redirect('home')


@login_required
def delete_server(request, instance_id):
    ec2 = boto3.client('ec2', region_name='us-west-2')
    response = ec2.terminate_instances(
        InstanceIds=[
            instance_id
        ]
    )
    server = Server.objects.filter(instance_id=instance_id)
    server.delete()
    return redirect('home')


@login_required
def start_server(request, instance_id):
    # Start server on AWS
    ec2 = boto3.client('ec2', region_name='us-west-2')
    response = ec2.start_instances(
        InstanceIds=[
            instance_id
        ]
    )
    # Update Server object in DB
    server = Server.objects.filter(instance_id=instance_id).first()
    server.update_times_start()
    server.save()
    return redirect('home')


@login_required
def stop_server(request, instance_id):
    # Stop server on AWS
    ec2 = boto3.client('ec2', region_name='us-west-2')
    response = ec2.stop_instances(
        InstanceIds=[
            instance_id
        ]
    )
    # Update Server object in DB:
    server = Server.objects.filter(instance_id=instance_id).first()
    server.update_times_stop()
    server.save()
    return redirect('home')


def list_schedules(request):
    schedules = Schedule.objects.all()
    return render(request, 'game_server_management/list-schedules.html', {'schedules': schedules})


def create_update_schedule(request, id=None):
    if request.method == 'GET':
        if id:
            schedule = Schedule.objects.get(id=id)
            form = ScheduleCreationForm(instance=schedule)
            return render(request, 'game_server_management/create-schedule.html',
                          {'form': form, 'schedule': schedule})
        else:
            return render(request, 'game_server_management/create-schedule.html',
                          {'form': ScheduleCreationForm()})
    else:
        try:
            if id:
                schedule = Schedule.objects.get(id=id)
                form = ScheduleCreationForm(request.POST, instance=schedule)
            else:
                form = ScheduleCreationForm(request.POST)
            new_schedule = form.save(commit=False)
            new_schedule.save()
            return redirect('list_schedules')
        except ValueError:
            return render(request, 'game_server_management/create-schedule.html',
                          {'form': ScheduleCreationForm(),
                           'error': 'Some data submitted was invalid; please correct and try again.'})
