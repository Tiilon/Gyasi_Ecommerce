from django.urls import path
from .views import *

app_name = "main_site"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("category", CategoryView.as_view(), name="category"),
    path("items", ItemsView.as_view(), name="items"),
    path("cart", CartView.as_view(), name="cart"),
    path("checkout", CheckoutView.as_view(), name="checkout"),
]
