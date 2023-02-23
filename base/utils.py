from django.conf import settings
from django.core.mail import send_mail,EmailMultiAlternatives




def send_account_activation_email(email , email_token):
    email_from = settings.EMAIL_HOST_USER
    urlx = f"{settings.DEFAULT_DOMAIN}/user/activate/{email_token}"
    subject, from_email, to = ('Your account needs to be verified',email_from,f"{email}",)
    text_content = "This is an important message."
    html_content = f"<h1>Thanks for joining our platform</h1><p>click to verify:{urlx}</p><p>After clicking the link. You may be required to log in with the details you provided</p>"
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    return msg.send()