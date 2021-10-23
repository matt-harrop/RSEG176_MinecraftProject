from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect


# Create your views here.

# Authentication


def login_user(request):
    if request.method == 'GET':
        return render(request, 'authentication/login.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user is None:
            return render(request, 'authentication/login.html',
                          {'form': AuthenticationForm(), 'error': 'Username and password combination is invalid.'})
        else:
            login(request, user)
            return redirect('home')


def register_user(request):
    if request.method == 'GET':
        return render(request, 'authentication/register.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('home')
            except IntegrityError:
                return render(request, 'authentication/register.html', {
                    'form': UserCreationForm(),
                    'error': 'Username supplied is already in use - please select another.'
                })
        else:
            # Tell the use that their passwords did not match.
            return render(request, 'authentication/register.html', {
                'form': UserCreationForm(),
                'error': 'Passwords supplied did not match.'
            })


def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
        # return render(request, 'authentication/login.html',
        #               {'form': UserCreationForm(), 'message': 'You have been logged out successfully.'})
