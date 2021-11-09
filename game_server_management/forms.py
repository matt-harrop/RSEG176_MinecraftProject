from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm

from game_server_management.models import Schedule


class AuthenticationFormWithInactiveUsersOkay(AuthenticationForm):
    def confirm_login_allowed(self, user):
        pass

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
            'start_time': forms.DateTimeInput(
                # attrs={
                #     'class': 'form-control'
                # }
            ),
            'end_time': forms.DateTimeInput(
                # attrs={
                #     'class': 'form-control'
                # }
            ),
            'days': forms.SelectMultiple(
                # attrs={
                #     'class': 'form-control'
                # }
            )
        }