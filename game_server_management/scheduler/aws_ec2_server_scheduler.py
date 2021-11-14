import boto3

from game_server_management.models import Schedule, Server
from datetime import time, datetime


# Method to get all the servers that need to be turned on/off?
# Then update the start/stop times on all the servers in DB.

def start_servers(servers):
    instance_ids = []
    for server in servers:
        instance_ids.append(server.instance_id)
        server.update_times_start()
    # Start servers on AWS
    ec2 = boto3.client('ec2', region_name='us-west-2')
    response = ec2.start_instances(
        InstanceIds=instance_ids
    )
#     Should check here for success of starting/stopping for updating servers, probably.

def stop_servers(servers):
    instance_ids = []
    for server in servers:
        instance_ids.append(server.instance_id)
        server.update_times_stop()
    # Stop servers on AWS
    ec2 = boto3.client('ec2', region_name='us-west-2')
    response = ec2.stop_instances(
        InstanceIds=instance_ids
    )
#     Should check here for success of starting/stopping for updating servers, probably.


def start_stop_servers():
    # Get next 15 minute mark:
    current_time = datetime.now().time().replace(second=0)
    current_day = datetime.now().strftime("%a")
    while divmod(current_time.minute, 15)[1] != 0:
        current_time.replace(minute=current_time.minute + 1)
    # Start servers on a schedule with a matching start_time:
    results = Server.objects.filter(schedule__start_time=current_time)
    # Filter results down to match the current day as well:
    servers_to_start = []
    for server in results:
        # Days is stored as a JSON object, containing a single list which contains a single string
        # which includes a list of comma-separated 3-character days, e.g. '["Mon,Tue,Sat"]'
        if current_day in server.schedule.days[0]:
            servers_to_start.append(server)
    start_servers(servers_to_start)
    # Stop servers on a schedule with a matching stop time:
    results2 = Server.objects.filter(schedule__end_time=current_time)
    servers_to_stop = []
    for server in results2:
        # Days is stored as a JSON object, containing a single list which contains a single string
        # which includes a list of comma-separated 3-character days, e.g. '["Mon,Tue,Sat"]'
        if current_day in server.schedule.days[0]:
            servers_to_stop.append(server)
    stop_servers(servers_to_stop)
