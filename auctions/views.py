from unicodedata import category
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Category, User, Product, Bid, Comment

def index(request):
    if request.user.is_authenticated:
        Watchlist = request.user.watchlist.all()
    else:
        Watchlist = None
    return render(request, "auctions/index.html", {
        "Products": Product.objects.all(),
        "Watchlist": Watchlist
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
    CategoryList = Category.objects.all()
    if request.method == "POST":
        Product_name = request.POST["name"]
        Product_price = request.POST["price"]
        Product_description = request.POST["description"]
        Product_image = request.FILES["image"]
        Product_category = Category.objects.get(pk=int(request.POST["categories"]))
        newProduct = Product.objects.create(
            name = Product_name,
            price = Product_price,
            description = Product_description,
            image = Product_image,
            close = False,
            category = Product_category,
            created_by = request.user
        )
        return HttpResponseRedirect(reverse("auctions:listings", args=(newProduct.id,)))
    return render(request, "auctions/create.html", {
        "CategoryList": CategoryList
    })    


def listings(request, product_id):
    listings = Product.objects.get(pk=product_id)
    BidList = listings.product_bids.values_list("bid", flat=True)
    BidderList = list(listings.product_bids.values_list("user_id", flat=True))
    CommentList = listings.product_comment.all()
    CategoryList = Category.objects.all().values_list('name', flat=True)
    
    # Check if user is signed in or not, if not, the watchlist feature won't be showed
    if request.user.is_authenticated:
        watchlist = request.user.watchlist.all()
    else:
        watchlist = None
    
    # Check if anyone bid on this listing, if yes, the last bidder will be the winner
    if not BidderList:
        winner = "No one has bid on this listing"
    else:
        winner = User.objects.get(pk = BidderList[-1])
        
    # Check if anyone bid on this listing, if no, the current bid is the starting bid, else, the current bid will be the max value of the bid list
    if not BidList:
        maxBidPrice = listings.price
    else:
        maxBidPrice = float(max(BidList))
    
    # Return the listing info to the template 
    if listings is not None:
        return render(request,'auctions/listings.html', {
            'listings': listings,
            'bidding_history': listings.product_bids.all(),
            'maxBidPrice': format(maxBidPrice,".2f"),
            'winner': winner,
            'commentList': CommentList,
            "Watchlist": watchlist,
            "CategoryList": CategoryList
            })
    else:
        raise Http404('Product does not exist')
    
@login_required    
def bidding(request, product_id):
    if request.method == "POST":
        listings = Product.objects.get(pk=product_id)
        newInput = float(request.POST['bidding'])
        
        # Check if the user input is valid (must be greater than the starting bid), if not, return an error message
        if newInput > listings.price:
            
            #Create a BidPriceList list to store all the bidding history
            BidPriceList = listings.product_bids.values_list("bid", flat=True)
            
            # Check if the BidPriceList is empty, if yes, the maxBidPrice is the starting bid, if not, the maxBidPrice is the max value in the BidPriceList
            if not BidPriceList:
                maxBidPrice = listings.price
            else:
                maxBidPrice = float(max(BidPriceList))
                
            # Check if the user input is valid (must be greater than the maxBid), if valid, create a new bid
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

# This function is for adding listing to watchlist    
@login_required
def watchlist(request, product_id):
    listings = Product.objects.get(pk = product_id)
    watchlist = request.user.watchlist.all()
    if listings in watchlist:
        listings.in_watchlist.remove(request.user)
    else:
        listings.in_watchlist.add(request.user)
    return HttpResponseRedirect(reverse('auctions:listings', kwargs={'product_id': listings.id}))

# This function is for showing the watchlist
@login_required
def showWatchList(request):
    return render (request, "auctions/watchlist.html", {
        "Watchlist": request.user.watchlist.all()
    })

def showCategories(request):
    CategoryList = Category.objects.all()
    return render(request, "auctions/categories.html", {
        'CategoryList': CategoryList
    })
    
def Categories(request, categories_id):
    category = Category.objects.get(pk = categories_id)
    category_listing = category.categories.all()
    return render(request, "auctions/category.html", {
        'category_listing': category_listing,
        'category': category
    })