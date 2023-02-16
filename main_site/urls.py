from django.urls import path
from .views import *

app_name = "main_site"

urlpatterns = [
    path("", ProductView.as_view(), name="items"),
    path("category", ProductCategoryView.as_view(), name="category"),
    path("category/<int:cart_id>/", ProductCategoryView.as_view(), name="category_detail"),
    path("category-items/<int:cart_id>", ProductView.as_view(), name="category_items"),
    path("delete-cart/<int:cart_id>", delete_cart, name="delete_cart"),
    path("product-search", search_product, name="product_search"),
    path("get-product-details/<int:product_id>", get_product_details, name="get_product_details"),
    path("get-cart-items", get_cart_items, name="get_cart_items"),
    path("add-cart-item/<int:product_id>", add_cart_item, name="add_cart_item"),
    path("cart", CartView.as_view(), name="cart"),
]
