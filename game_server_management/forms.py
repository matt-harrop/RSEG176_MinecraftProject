from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm
from datetime import time

from game_server_management.models import Schedule


class AuthenticationFormWithInactiveUsersOkay(AuthenticationForm):
    def confirm_login_allowed(self, user):
        pass


def get_time_choices():
    times = []
    for hour in range(24):
        for minute_mark in range(0, 46, 15):
            time_obj = time(hour, minute_mark)
            times.append(tuple([time_obj, time_obj.strftime('%I:%M %p')]))
    return times

# [
#     ('orange', 'Oranges'),
#     ('cantaloupe', 'Cantaloupes'),
#     ('mango', 'Mangoes'),
#     ('honeydew', 'Honeydews'),
# ]


class ScheduleCreationForm(ModelForm):
    class Meta:
        model = Schedule
        fields = ['name', 'start_time', 'end_time', 'days']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'start_time': forms.Select(
                choices=get_time_choices(),
                attrs={
                    'class': 'form-select'
                }
            ),
            'end_time': forms.Select(
                choices=get_time_choices(),
                attrs={
                    'class': 'form-select'
                }
            ),
            'days': forms.SelectMultiple(
                attrs={
                    'class': 'form-select'
                }
            )
        }
