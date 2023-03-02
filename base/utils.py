from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect


def send_account_activation_email(email , email_token):
    email_from = settings.EMAIL_HOST_USER
    urlx = f"{settings.DEFAULT_DOMAIN}/user/activate/{email_token}"
    subject, from_email, to = ('Your account needs to be verified',email_from,f"{email}",)
    text_content = "This is an important message."
    html_content = f"<h1>Thanks for joining our platform</h1><p>click to verify:{urlx}</p><p>After clicking the link. You may be required to log in with the details you provided</p>"
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

