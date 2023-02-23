from django.conf import settings
from twilio.rest import Client

class MessageHandler:
    phone_number = None
    otp = None
    
    def __init__(self,phone_number,otp):
        self.phone_number = phone_number
        self.otp = otp
        
    def send_otp_on_phone(self):
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        
        client = Client(account_sid, auth_token)

        message = client.messages.create(body=self.otp,from_='+15017122661',to=self.phone_number)