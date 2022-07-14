from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return f"{self.username}"
    
class Category(models.Model):
    name = models.CharField(max_length=256)
    
    def __str__(self):
        return f"{self.name}"

class Product(models.Model):
    name = models.CharField(max_length=256)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(default='', blank=True)
    image = models.ImageField(upload_to='auctions/media', null = True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="categories")
    created_at = models.DateTimeField(auto_now_add=True)
    close = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_created", default=1)
    in_watchlist = models.ManyToManyField(User, blank=True ,related_name="watchlist")
    
    def __str__(self):
        return f"{self.name}"
    
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="UserBid")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_bids")
    bid = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return f"{self.user} bid ${self.bid} on {self.product}"
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comment")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_comment")
    comment = models.TextField(blank=False)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user}: {self.comment}"
    