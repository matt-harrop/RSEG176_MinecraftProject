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


# 2021-10-26 18:16:20 GMT