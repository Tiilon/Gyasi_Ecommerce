from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_account_activation_email(email , email_token, domain):
    email_from = settings.EMAIL_HOST_USER
    subject, from_email, to = ('Verify your account',email_from,f"{email}",)
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

def send_winner_email(email, product):
    email_from = settings.EMAIL_HOST_USER
    subject, from_email, to = ('Winner',email_from,f"{email}",)
    text_content = "Congratulations."
    html_content = f"<h1>We would like to congratulate you for being the winner of {product} Thanks for joining our participating</h1>"
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    return msg.send()

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

