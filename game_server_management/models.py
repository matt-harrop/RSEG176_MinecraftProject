import json

import boto3
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
import calendar

# Create your models here.
from pkg_resources import resource_filename


class Server(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    instance_id = models.CharField(max_length=200)

    def get_max_monthly_cost(self):
        # Get current price for a given instance, region and os
        price = float(get_price(get_region_name('us-west-2'), 't2.medium', 'Linux'))
        now = datetime.now()
        days_in_current_month = calendar.monthrange(now.year, now.month)[1]
        max_monthly_cost = days_in_current_month * 24 * price
        return f'{max_monthly_cost:.2f}'

    def get_current_monthly_cost(self):
        return 0



# HELPER METHODS

# Get current AWS price for an on-demand instance
def get_price(region, instance, os):
    # Search product filter
    FLT = '[{{"Field": "tenancy", "Value": "shared", "Type": "TERM_MATCH"}},' \
          '{{"Field": "operatingSystem", "Value": "{o}", "Type": "TERM_MATCH"}},' \
          '{{"Field": "preInstalledSw", "Value": "NA", "Type": "TERM_MATCH"}},' \
          '{{"Field": "instanceType", "Value": "{t}", "Type": "TERM_MATCH"}},' \
          '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}},' \
          '{{"Field": "capacitystatus", "Value": "Used", "Type": "TERM_MATCH"}}]'

    # Use AWS Pricing API at US-East-1
    client = boto3.client('pricing', region_name='us-east-1')

    f = FLT.format(r=region, t=instance, o=os)
    data = client.get_products(ServiceCode='AmazonEC2', Filters=json.loads(f))
    od = json.loads(data['PriceList'][0])['terms']['OnDemand']
    id1 = list(od)[0]
    id2 = list(od[id1]['priceDimensions'])[0]
    return od[id1]['priceDimensions'][id2]['pricePerUnit']['USD']


# Translate region code to region name
def get_region_name(region_code):
    default_region = 'EU (Ireland)'
    endpoint_file = resource_filename('botocore', 'data/endpoints.json')
    try:
        with open(endpoint_file, 'r') as f:
            data = json.load(f)
        return data['partitions'][0]['regions'][region_code]['description']
    except IOError:
        return default_region
