from django.urls import path
from .views import *

app_name = "main_site"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("category", ProductCategoryView.as_view(), name="category"),
    path("category/<int:cart_id>/", ProductCategoryView.as_view(), name="category_detail"),
    path("items", ProductView.as_view(), name="items"),
    path("cart", CartView.as_view(), name="cart"),
    path("checkout", CheckoutView.as_view(), name="checkout"),
]
