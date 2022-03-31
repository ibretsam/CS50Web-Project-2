from distutils.command.upload import upload
from email.mime import image
from pyexpat import model
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Product(models.Model):
    name = models.CharField(max_length=256)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(default='')
    
    def __str__(self):
        return f"{self.id}:\n \t\t{self .name}\n \t\t{self.price}\n \t\t{self.description}\n"