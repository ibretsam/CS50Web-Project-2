import imp
from django.contrib import admin

from .models import Product, User, Bid, Comment


# Register your models here.
admin.site.register(Product)
admin.site.register(User)
admin.site.register(Bid)
admin.site.register(Comment)