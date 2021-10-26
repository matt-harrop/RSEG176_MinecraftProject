from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_new_server, name='create_server'),
    path('start/<str:instance_id>', views.start_server, name='start_server'),
    path('stop/<str:instance_id>', views.stop_server, name='stop_server'),

]
