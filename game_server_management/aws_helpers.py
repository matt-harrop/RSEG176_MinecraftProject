import json
import boto3
from pkg_resources import resource_filename


# Get current AWS price for an on-demand instance
def get_on_demand_instance_price(region, instance, os):
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
    default_region = 'US West (Oregon)'
    endpoint_file = resource_filename('botocore', 'data/endpoints.json')
    try:
        with open(endpoint_file, 'r') as f:
            data = json.load(f)
        return data['partitions'][0]['regions'][region_code]['description']
    except IOError:
        return default_region
