from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render


# Create your views here.

@login_required
def home(request):
    return render(request, 'game_server_management/index.html')
