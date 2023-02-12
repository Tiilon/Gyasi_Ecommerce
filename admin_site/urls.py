from django.urls import path
from .views import *

app_name = "admin_site"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("cart/", CategoryView.as_view(), name="category"),
    path("cart-all/", get_categories, name="all_categories"),
    path("change-cart-status/<cart_id>", change_cart_status, name="change_cart_status"),
    path("delete/<cart_id>", delete_cart, name="delete_cart"),
    path("product-list/", ProductListView.as_view(), name="get_product_list"),
    path("product-list/<int:cart_id>", ProductListView.as_view(), name="get_cart_product_list"),
    path("create-product/", create_product, name="create_product"),
]
