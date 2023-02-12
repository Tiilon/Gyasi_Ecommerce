from django.db import models
from user.models import User
from datetime import datetime
from django_resized import ResizedImageField


class ProductCategoryModel(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    status = models.BooleanField(default=True)
    cart_sm_image = ResizedImageField(
        size=[150, 150], upload_to="user/cart_sm_image", blank=True, null=True
    )
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def get_data(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_by': self.created_by.email
        }


class ProductModel(models.Model):
    category = models.ForeignKey(
        ProductCategoryModel,
        related_name="products",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=250, blank=True, null=True)
    status = models.BooleanField(default=True)
    ticket_price = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ProductImageModel(models.Model):
    product = models.ForeignKey(
        ProductModel,
        related_name="images",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to="images/original/product_image", blank=True, null=True)
    resized_image = ResizedImageField(
        size=[500, 500], upload_to="images/resized/product_image", blank=True, null=True
    )
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now)


class CartItem(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.FloatField(blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product} - {self.quantity}"
