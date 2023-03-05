from django.urls import path
from .views import *

app_name = "management"

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
    path("update-product/<int:product_id>", update_product, name="update_product"), # pyright: ignore
    path("delete-product/<product_id>", delete_product, name="delete_product"),
    path("delete-image/<image_id>", delete_product_image, name="delete_product_image"),
    path("payments-all/", payment_page, name="all_payments"),
    path("payments/", get_tickets, name="all_sales"),
]
