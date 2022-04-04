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
    path("listings/<int:product_id>", views.listings, name="listings")
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
