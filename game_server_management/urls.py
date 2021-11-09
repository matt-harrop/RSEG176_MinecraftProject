from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_new_server, name='create_server'),
    path('delete/<str:instance_id>', views.delete_server, name='delete_server'),
    path('start/<str:instance_id>', views.start_server, name='start_server'),
    path('stop/<str:instance_id>', views.stop_server, name='stop_server'),
    path('schedules/', views.list_schedules, name='list_schedules'),
    path('schedules/create', views.create_update_schedule, name='create_schedule'),
    path('schedules/<int:id>/update', views.create_update_schedule, name='update_schedule'),
]
