from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Server(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    instance_id = models.CharField(max_length=200)
