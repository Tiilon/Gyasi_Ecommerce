from django.shortcuts import get_object_or_404, redirect, render
from .forms import PaymentForm
from django.conf import settings
from .models import Payment
from django.contrib import messages

def initiate_payment(request):
    if request.method == "POST":
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            payment = payment_form.save()
            return render(request,'payment/make_payment.html',{'payment':payment, 'public_key':settings.PAYSTACK_PUBLIC_KEY})
    else:
        payment_form = PaymentForm()
        return render(request,'payment/initiate_payment.html',{'payment':payment_form})
        
        
def verify_payment(request, ref):
    payment = get_object_or_404(Payment, reference=ref)
    verified = payment.verify_payment()
    print(payment.verified)
    if verified:
        messages.success(request,"Verification successful")
    else:
        messages.error(request,"Verification failed")
    return redirect('payment_app:new_payment')