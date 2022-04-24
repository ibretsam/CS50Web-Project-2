from email.mime import image
from unicodedata import name
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Product, Bid, Comment

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
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


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
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")
    
@login_required
def create(request):
    if request.method == "POST":
        Product_name = request.POST["name"]
        Product_price = request.POST["price"]
        Product_description = request.POST["description"]
        Product_image = request.FILES["image"]
        newProduct = Product.objects.create(
            name = Product_name,
            price = Product_price,
            description = Product_description,
            image = Product_image,
            close = False
        )
        return HttpResponseRedirect(reverse("auctions:listings", args=(newProduct.id,)))
    return render(request, "auctions/create.html")    


def listings(request, product_id):
    listings = Product.objects.get(pk=product_id)
    BidList = listings.product_bids.values_list("bid", flat=True)
    BidderList = list(listings.product_bids.values_list("user_id", flat=True))
    CommentList = listings.product_comment.all()
    if not BidderList:
        winner = "No one has bid on this listing"
    else:
        winner = User.objects.get(pk = BidderList[-1])
    if not BidList:
        maxBidPrice = listings.price
    else:
        maxBidPrice = float(max(BidList))
    if listings is not None:
        return render(request,'auctions/listings.html', {
            'listings': listings,
            'bidding_history': listings.product_bids.all(),
            'maxBidPrice': format(maxBidPrice,".2f"),
            'winner': winner,
            'commentList': CommentList
            })
    else:
        raise Http404('Product does not exist')
    
@login_required    
def bidding(request, product_id):
    if request.method == "POST":
        listings = Product.objects.get(pk=product_id)
        newInput = float(request.POST['bidding'])
        if newInput > listings.price:
            BidPriceList = listings.product_bids.values_list("bid", flat=True)
            if not BidPriceList:
                maxBidPrice = listings.price
            else:
                maxBidPrice = float(max(BidPriceList))
            if newInput > maxBidPrice:
                newBid = Bid.objects.create(
                    product = Product.objects.get(pk=product_id),
                    user = request.user,
                    bid = request.POST['bidding'])
                return HttpResponseRedirect(reverse('auctions:listings', kwargs={'product_id': newBid.product.id,} ))
            else:
                return render(request, "auctions/error.html", {'error_message': "Your bid must greater than the current bid"})
        else:
            return render(request, "auctions/error.html", {'error_message': "Your bid must greater than the starting bid"})
        
@login_required
def close(request, product_id):
    if request.method == "POST":
        listings = Product.objects.get(pk = product_id)
        if request.user == listings.created_by:
            listings.close = True
            listings.save()
            return HttpResponseRedirect(reverse('auctions:listings', kwargs={'product_id': listings.id}))
        
@login_required
def comment(request, product_id):
    if request.method == "POST":
        listing = Product.objects.get(pk = product_id)
        user_comment = request.user
        content = request.POST["comment"]
        newComment = Comment.objects.create(
            user = user_comment,
            product = listing,
            comment = content
        )
        return HttpResponseRedirect(reverse('auctions:listings', kwargs={'product_id': listing.id}))