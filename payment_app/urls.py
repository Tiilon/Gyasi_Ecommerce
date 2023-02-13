from django.urls import path
from .views import *

app_name = "payment_app"

urlpatterns = [
    path("", initiate_payment, name="new_payment"), #pyright:ignore
    path("p/<str:ref>", verify_payment, name="verify_payment"),
]
