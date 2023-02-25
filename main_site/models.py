from django.db import models
from base.utils import send_winner_email
from payment_app.models import Payment
from user.models import User
from datetime import datetime
from django_resized import ResizedImageField
from base.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
import random


class ProductCategoryModel(BaseModel):
    name = models.CharField(max_length=250, blank=True, null=True)
    cart_sm_image = ResizedImageField(
        size=[150, 150], upload_to="user/cart_sm_image", blank=True, null=True
    )
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
    
    def get_data(self):
        return {
            'id': self.id, # pyright: ignore
            'name': self.name,
            'created_by': self.created_by.email # pyright: ignore
        }


class ProductModel(BaseModel):
    category = models.ForeignKey(
        ProductCategoryModel,
        related_name="products",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    actual_price = models.IntegerField(default=0)
    ticket_price = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
    
    def number_of_tickets(self) -> int:
        return round(self.actual_price/self.ticket_price)

class ProductImageModel(BaseModel):
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
    product_admin_size = ResizedImageField(
        size=[1098, 717], upload_to="images/resized/product_image", blank=True, null=True
    )
    

class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True)
    payment_id = models.ForeignKey(Payment, on_delete=models.CASCADE, blank=True, null=True)
    paid = models.BooleanField(default=False)
    

    def __str__(self):
        return f"{self.product} - {self.quantity}"

class TicketModel(BaseModel):
    user = models.ForeignKey(User, related_name="user_tickets",on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel, related_name="product_tickets", on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return self.user.email
    
@receiver(post_save , sender = TicketModel)
def get_winning_ticket(sender , instance , created , **kwargs):
    try:
        if created:
            number_of_tickets = instance.product.number_of_tickets() #pyright:ignore
            product_tickets = instance.product.product_tickets.filter(status=False).order_by("created_at")[:10] #pyright:ignore
            if product_tickets.count() == number_of_tickets:
                ticket_ids = [ticket.uid for ticket in product_tickets]
                selected_id = random.choice(ticket_ids)
                selected_ticket = TicketModel.objects.get(uid=selected_id)
                email = selected_ticket.user.email
                product = selected_ticket.product.name #pyright:ignore
                send_winner_email(email, product)
                for i in product_tickets:
                    i.status = True
                    i.save()

    except Exception as e:
        print(e)