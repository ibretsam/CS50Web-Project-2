from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Product, Bid

class newBidForm(forms.Form):
    input = forms.FloatField()


def index(request):
    return render(request, "auctions/index.html", {
        "Products": Product.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    

def create(request):
    return render(request, "auctions/create.html")    


def listings(request, product_id):
    listings = Product.objects.get(pk=product_id)
    if listings is not None:
        return render(request,'auctions/listings.html', {
            'listings': listings,
            'bidding_history': listings.ProductBid.all(),
            })
    else:
        raise Http404('Product does not exist')
    
@login_required    
def bidding(request, product_id):
    if request.method == "POST":
        newBid = Bid.objects.create(
        product = Product.objects.get(pk=product_id),
        user = request.user,
        bid = request.POST['bidding'])
        
    return HttpResponseRedirect(reverse('auctions:listings', args=(newBid.product.id,)))