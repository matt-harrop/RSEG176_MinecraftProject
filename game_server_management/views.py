from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
import boto3

# Create your views here.

@login_required
def home(request):
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances()
    instanceName = response['Reservations'][0]['Instances'][0]['KeyName']

    return render(request, 'game_server_management/index.html', {'instanceName': instanceName})
