import random
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from celery import shared_task
from time import sleep
from main_site.models import Cart, TicketModel
from payment_app.models import Payment
from user.models import User

@shared_task
def send_account_activation_email(email , email_token):
    email_from = settings.EMAIL_HOST_USER
    urlx = f"{settings.DEFAULT_DOMAIN}/user/activate/{email_token}"
    subject, from_email, to = ('Your account needs to be verified',email_from,f"{email}",)
    text_content = "This is an important message."
    html_content = f"<h1>Thanks for joining our platform</h1><p>click to verify:{urlx}</p><p>After clicking the link. You may be required to log in with the details you provided</p>"
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    return msg.send()

@shared_task
def send_winner_email(email, product):
    email_from = settings.EMAIL_HOST_USER
    subject, from_email, to = ('Winner',email_from,"lovodol495@youke1.com",)
    # subject, from_email, to = ('Winner',email_from,f"{email}",)
    text_content = "Congratulations."
    html_content = f"<h1>We would like to congratulate you for being the winner of {product} Thanks for joining our participating</h1>"
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    return msg.send()

@shared_task
def send_payment_receipt(email, item_list):
    email_from = settings.EMAIL_HOST_USER
    subject, from_email, to = ('Receipt',email_from,f"{email}",)
    context = {
        'test':"Test",
        "content":"You have made payments for the following items",
        "items":item_list
    }
    html_content = render_to_string("email/receipt_emails.html", context)
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    return msg.send()


@shared_task
def create_ticket(user_id, payment_id):
    user = User.objects.get(id=user_id)
    payment = Payment.objects.get(id=payment_id)
    item_list = []
    cart_items = Cart.objects.filter(user=user, paid=False)
    for item in cart_items:
        for _ in range(item.quantity):
            new_ticket = TicketModel.objects.create(
                user = item.user,
                product = item.product,
            )
            number_of_tickets = new_ticket.product.number_of_tickets() #pyright:ignore
            product_tickets = new_ticket.product.product_tickets.filter(status=False).order_by("created_at")[:10] #pyright:ignore
            if product_tickets.count() == number_of_tickets:
                ticket_ids = [ticket.uid for ticket in product_tickets]
                selected_id = random.choice(ticket_ids)
                selected_ticket = TicketModel.objects.get(uid=selected_id)
                email = selected_ticket.user.email
                product = selected_ticket.product.name #pyright:ignore
                send_winner_email.delay(email, product)
                selected_ticket.is_winner = True
                selected_ticket.save()
                for i in product_tickets:
                    i.status = True
                    i.save()
            
        if not item.paid:
            item.paid = True
            item.status = False
            item.payment_id = payment #pyright:ignore
            item.save()
            item_detail = {
                'product':item.product.name, #pyright:ignore
                'quantity': item.quantity,
                'price':item.price
            }
            item_list.append(item_detail)
    send_payment_receipt.delay(user.email, item_list)  # type: ignore
    return True