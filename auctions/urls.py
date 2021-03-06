from unicodedata import name
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listings/<int:product_id>", views.listings, name="listings"),
    path("listings/<int:product_id>/bid", views.bidding, name="bidding"),
    path("listings/<int:product_id>/close", views.close, name="close"),
    path("listings/<int:product_id>/comment", views.comment, name="comment"),
    path("listings/<int:product_id>/watchlist", views.watchlist, name="watchlist"),
    path("watchlist", views.showWatchList, name="showWatchlist"),
    path("categories", views.showCategories, name="categories"),
    path("categories/<int:categories_id>", views.Categories, name="category")
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
