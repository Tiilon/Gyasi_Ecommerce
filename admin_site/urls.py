from django.urls import path
from .views import *

app_name = "admin_site"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("cart/", CategoryView.as_view(), name="category"),
    path("cart-all/", get_categories, name="all_categories"),
    path("change-cart-status/<cart_id>", change_cart_status, name="change_cart_status"),
    path("get-cart-details/<cart_id>", get_cart_details, name="get_cart_details"),
    path("update-cart-details/<cart_id>", update_cart, name="update_cart"),
    path("delete/<cart_id>", delete_cart, name="delete_cart"),
    path("product-list/", ProductListView.as_view(), name="get_product_list"),
    path("product-list/<int:cart_id>", ProductListView.as_view(), name="get_cart_product_list"),
    path("product-details/<int:product_id>", get_product_details, name="get_product_details"),
    path("create-product/", create_product, name="create_product"), # pyright: ignore
]
