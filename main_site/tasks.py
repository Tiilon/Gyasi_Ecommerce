import random
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from celery import shared_task
from main_site.models import ProductModel, TicketModel
from user.models import User

@shared_task
def send_account_activation_email(email , email_token, domain):
    email_from = settings.EMAIL_HOST_USER
    subject, from_email, to = ('Verify your account',email_from,email)
    context = {
        'test':"Account activation",
        "token":email_token,
        "domain":domain
    }
    html_content = render_to_string("email/verification_mail.html", context)
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    return msg.send()

@shared_task
def send_winner_email(email, product):
    email_from = settings.EMAIL_HOST_USER
    subject, from_email, to = ('Winner',email_from,email,)
    context = {
        'test':"Winner Confirmation",
        "product":product
    }
    text_content = "Congratulations."
    html_content = render_to_string("email/winner_mail.html", context)
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
def create_ticket(item_qty, user_id, product_id):
    for _ in range(item_qty):
        new_ticket = TicketModel.objects.create(
            user = User.objects.get(id=user_id),
            product = ProductModel.objects.get(id=product_id),
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
                i.status = True #tickets used
                i.save()
    return True
