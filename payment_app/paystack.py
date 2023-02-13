from django.conf import settings
import requests

class PayStack:
    PAYSTACK_SECRET_KEY = 'sk_test_3ac72326897a976aa05beda1f1bbe6cbeb1235bd'
    base_url = 'https://api.paystack.co'
    
    def verify_payment(self, ref, *args, **kwargs):
        path = f'/transaction/verify/{ref}'
        
        headers = {
            "Authorization": f"Bearer {self.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        url = self.base_url + path
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            return response_data['status'], response_data['data']
        response_data = response.json()
        return response_data['status'], response_data['message']