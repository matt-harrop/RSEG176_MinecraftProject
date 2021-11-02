import boto3
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
import calendar
from .aws_helpers import *

from django.utils import timezone

from .aws_helpers import get_on_demand_instance_price, get_region_name

# Create your models here.
from pkg_resources import resource_filename


class Server(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    instance_id = models.CharField(max_length=200)
    last_stop_time = models.DateTimeField(null=True)
    last_start_time = models.DateTimeField(default=timezone.now)
    billing_hours_running_total = models.IntegerField(default=0)
    billing_hours_month = models.IntegerField(default=1)

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
