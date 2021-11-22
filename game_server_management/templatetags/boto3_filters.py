from django import template
from datetime import datetime
import re

from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def get_state_change_timestamp(value, arg="%m/%d"):
    if value:
        match = re.search('(?<=\().*(?=\))', value)
        time_obj = datetime.strptime(match.group(), "%Y-%m-%d %H:%M:%S %Z")
        return time_obj.strftime(arg)
    else:
        return value


@register.filter
@stringfilter
def instance_desc(value):
    descriptions = {
        "t2.medium": "Teeny",
        "t2.large": "Standard",
        "t2.xlarge": "Standard",
        "t2.2xlarge": "Behemoth"
    }
    if descriptions[value]:
        return descriptions[value]
    else:
        return value
