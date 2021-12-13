import boto3
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime, timedelta
import calendar
from .aws_helpers import *
from django.utils.translation import gettext_lazy as _

from django.utils import timezone

from .aws_helpers import get_on_demand_instance_price, get_region_name

# Create your models here.
from pkg_resources import resource_filename


class Schedule(models.Model):
    name = models.CharField(max_length=200)
    start_time = models.TimeField()
    end_time = models.TimeField()

    # class DaysOfWeek(models.TextChoices):
    #     MONDAY = 'Mon', _('Monday')
    #     TUESDAY = 'Tue', _('Tuesday')
    #     WEDNESDAY = 'Wed', _('Wednesday')
    #     THURSDAY = 'Thu', _('Thursday')
    #     FRIDAY = 'Fri', _('Friday')
    #     SATURDAY = 'Sat', _('Saturday')
    #     SUNDAY = 'Sun', _('Sunday')

    days = models.JSONField()


class Server(models.Model):
    name = models.CharField(max_length=200)
    instance_id = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    last_stop_time = models.DateTimeField(null=True)
    last_start_time = models.DateTimeField(default=timezone.now)
    billing_hours_running_total = models.IntegerField(default=0)
    billing_hours_month = models.IntegerField(default=1)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, default=None, null=True)

    def get_max_monthly_cost(self):
        # Get current price for a given instance, region and os
        price = float(get_on_demand_instance_price(get_region_name('us-west-2'), 't2.medium', 'Linux'))
        now = datetime.now()
        days_in_current_month = calendar.monthrange(now.year, now.month)[1]
        max_monthly_cost = days_in_current_month * 24 * price
        return f'{max_monthly_cost:.2f}'

    def get_current_monthly_cost(self):
        # Get current state (running or not):
        ec2 = boto3.resource('ec2')
        instance = ec2.Instance(self.instance_id)

        total_billing_hours = 0
        hourly_cost = float(get_on_demand_instance_price(get_region_name('us-west-2'), 't2.medium', 'Linux'))

        if instance.state["Name"] == 'running':
            # get current period number of hours
            # make sure to go no further back then the start of the current month.

            first_of_month = datetime.now().replace(day=1, hour=0)
            instance_running_since_month_start = self.last_start_time.timestamp() < first_of_month.timestamp()
            if instance_running_since_month_start:
                start_time = first_of_month
                self.billing_hours_running_total = 0
                self.billing_hours_month = datetime.now().month
            else:
                start_time = self.last_start_time
            current_duration_ts = datetime.now().timestamp() - start_time.timestamp()
            # I believe timestamps are in seconds...
            current_duration_hours = divmod(current_duration_ts, 3600)[0]
            total_billing_hours += current_duration_hours

            # Does the running total for billing hours need to be added?

            if self.billing_hours_month == datetime.now().month:
                total_billing_hours += self.billing_hours_running_total

            # return total with stored monthly running total

            # Get pricing from AWS to return actual cost, not just billable hours:

            return f'{total_billing_hours * hourly_cost:.2f}'

        # State is not currently running:

        # If there is a running total for this month:
        elif self.billing_hours_month == datetime.now().month:
            return f'{self.billing_hours_running_total * hourly_cost:.2f}'

        # Otherwise, server is not currently running and there is no running total for the month:
        else:
            return f'{0.00}'

    def update_times_start(self):
        # Wipe running total if last stop time was the previous month.
        if self.last_stop_time and self.last_start_time.timestamp() < datetime.now().replace(day=1, hour=0).timestamp():
            self.billing_hours_running_total = 0
            self.billing_hours_month = datetime.now().month
        # Update last start time.
        self.last_start_time = datetime.now()

    def update_times_stop(self):
        first_of_month = datetime.now().replace(day=1, hour=0)
        if self.last_start_time.timestamp() < first_of_month.timestamp():
            start_time = first_of_month
            self.billing_hours_month = datetime.now().month
            self.billing_hours_running_total = 0
        else:
            start_time = self.last_start_time
        current_duration_ts = datetime.now().timestamp() - start_time.timestamp()
        # I believe timestamps are in seconds...
        current_duration_hours = divmod(current_duration_ts, 3600)[0]
        self.billing_hours_running_total += current_duration_hours
        self.last_stop_time = datetime.now()

    def get_monthly_bill(self):
        # Get the EC2 boto3 object:
        ec2 = boto3.resource('ec2')
        instance = ec2.Instance(self.instance_id)

        # Get S3 records that are related to this instance's start and stop events:
        # Actually, use the Cloudtrail resource to lookup the records stored in S3:

        cloudTrail = boto3.client('cloudtrail')
        # Small note regarding Cloudtrail and boto3:
        # As of 12/6/21, the 'lookupAttributes' field is a list, but boto3 only allows it to contain
        # one item at the moment (why even make it a list then?).
        start_times_response = cloudTrail.lookup_events(
            LookupAttributes=[
                {
                    'AttributeKey': 'ResourceName',
                    'AttributeValue': instance.instance_id
                },
                # {
                #     'AttributeKey': 'EventName',
                #     'AttributeValue': 'StartInstances'
                # }
            ],
            StartTime=datetime(2021, 12, 1),
            EndTime=datetime(2021, 12, 31),
            # EventCategory='Management',
            MaxResults=9999
        )
        end_times_response = cloudTrail.lookup_events(
            LookupAttributes=[
                {
                    'AttributeKey': 'ResourceName',
                    'AttributeValue': instance.instance_id
                },
                # {
                #     'AttributeKey': 'EventName',
                #     'AttributeValue': 'StopInstances'
                # }
            ],
            StartTime=datetime(2021, 12, 1),
            EndTime=datetime(2021, 12, 31),
            # EventCategory='Management',
            MaxResults=9999
        )
        start_times = []
        end_times = []
        for event in start_times_response["Events"]:
            # Since we can only get events using one attribute filter from Cloudtrail, we have to look
            # here to make sure we're just getting the start/stop events that we want:
            if event["EventName"] == "StartInstances":
                # This gets us the actual datetime object:
                start_times.append(event["EventTime"])
                # start_times.append(datetime.strftime(event["EventTime"], "%Y/%m/%d"))
        for event in end_times_response["Events"]:
            if event["EventName"] == "StopInstances":
                end_times.append(event["EventTime"])

        print("Start Times:" + str(start_times))
        print("Stop Times:" + str(end_times))

        # If the first time is an end-time, we add a time to the list that is the beginning of the month:

        start_times.sort()
        end_times.sort()

        # Need to add start/end times for when starts/stops occur outside of the current month:
        if not start_times:
            if end_times:
                start_times.insert(0, get_month_start())
            # This is if we have no start or end times:
            else:
                # Bill for the whole month if the instance is running:
                if instance.state == 'running':
                    start_times.append(get_month_start())
                    end_times.append(get_month_end())
        # This is if we have a start time but no end time:
        elif not end_times:
            end_times.insert(-1, get_month_end())

        # Need to check and see if we have any start times and any end times before comparing them:
        if start_times and end_times:
            if end_times[0] < start_times[0]:
                # now = datetime.now()
                # month_start = now.replace(month=12, day=1, hour=0, minute=0)
                # # The following line would get production results; above is for testing.
                # # month_start = now.replace(month=now.month-1, day=1, hour=0, minute=0)
                start_times.insert(0, get_month_start())

            # If the last time is a start-time, we add a time to the list that is the last moment of the month:

            if start_times[-1] > end_times[-1]:
                # now = datetime.now()
                # month_end = now.replace(month=12, day=31, hour=23, minute=59)
                # # Line below would be for production assuming this runs first of the month, above is for testing:
                # # month_end = datetime.replace(month=now.month-1, day=now.day-1, hour=23, minute=59)
                end_times.insert(-1, get_month_end())

        # Now that we have our times, we combine them into one sorted list.

        event_times = start_times + end_times
        event_times.sort()

        # Now we get the difference between each pair of start-stop times and combine those into one time period:

        billable_time = timedelta()

        for i, time in enumerate(event_times):
            if i % 2 == 0:
                timespan = event_times[i + 1] - time
                billable_time += timespan

        # Finally, we get the current AWS rate for the current instance and multiply it by this time period,
        # returning the result:

        hourly_cost = float(get_on_demand_instance_price(get_region_name('us-west-2'), instance.instance_type, 'Linux'))
        print(f"Hourly Cost: {hourly_cost}")
        print(f"Billable hours: {billable_time.total_seconds() / 3600}")
        billed_cost = hourly_cost * billable_time.total_seconds() / 3600

        # return start_times
        # return response
        return {"event_times": event_times, "billed_cost": '${:,.2f}'.format(billed_cost)}


def get_month_start():
    now = datetime.now()
    month_start = now.replace(month=12, day=1, hour=0, minute=0)
    # The following line would get production results; above is for testing.
    # month_start = now.replace(month=now.month-1, day=1, hour=0, minute=0)


def get_month_end():
    now = datetime.now()
    month_end = now.replace(month=12, day=31, hour=23, minute=59)
    # Line below would be for production assuming this runs first of the month, above is for testing:
    # month_end = datetime.replace(month=now.month-1, day=now.day-1, hour=23, minute=59)
