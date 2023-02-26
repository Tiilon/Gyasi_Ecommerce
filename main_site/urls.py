from django.urls import path
from .views import *

app_name = "main_site"

urlpatterns = [
    path("", ProductView.as_view(), name="items"),
    path("get-active-status/<status>/", get_product_by_filter , name="items"),
    # path("get-active-status/<status>/<cart_id>", get_product_by_status , name="items"),
    path("category", ProductCategoryView.as_view(), name="category"),
    path("product/<product_id>/", ProductDetailView.as_view(), name="product_detail"),
    path("category/<cart_id>/", ProductCategoryView.as_view(), name="category_detail"),
    path("category-items/<cart_id>", ProductView.as_view(), name="category_items"),
    path("product-search/<meta>", ProductView.as_view(), name="product_search_items"),
    path("delete-cart/<cart_id>", delete_cart, name="delete_cart"),
    path("product-search", search_product, name="product_search"), #type:ignore
    path("get-product-details/<product_id>", get_product_details, name="get_product_details"),
    path("get-cart-items", get_cart_items, name="get_cart_items"),
    path("add-cart-item/<product_id>", add_cart_item, name="add_cart_item"),
    path("cart", CartView.as_view(), name="cart"),
    path("checkout", CheckOutView.as_view(), name="checkout"),
]
