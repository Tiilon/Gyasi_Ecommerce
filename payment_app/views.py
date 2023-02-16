from django.shortcuts import get_object_or_404, redirect, render

from main_site.models import Cart
from .forms import PaymentForm
from django.conf import settings
from .models import Payment
from django.contrib import messages
from django.http import JsonResponse

def initiate_payment(request):
    if request.method == "POST":
        amount = request.POST.get('amount')
        email = request.POST.get('email')
        payment = Payment.objects.create(amount=amount, email=email)
        return JsonResponse({"message": "success", 'data': payment.reference})
        
        # return render(request,'payment/make_payment.html',{'payment':payment, 'public_key':settings.PAYSTACK_PUBLIC_KEY})
        
        
# def verify_payment(request, ref):
#     payment = get_object_or_404(Payment, reference=ref)
#     verified = payment.verify_payment()
#     print(payment.verified)
#     if verified:
#         messages.success(request,"Verification successful")
#     else:
#         messages.error(request,"Verification failed")
#     return redirect('payment_app:new_payment')

def verify_payment(request, ref):
    payment = get_object_or_404(Payment, reference=ref)
    verified = payment.verify_payment()
    if verified:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            if not item.paid:
                item.paid = True
                item.payment_id = payment.id #pyright:ignore
                item.save()
        return JsonResponse({"message": "success"})
    else:
        return JsonResponse({"message": "failed"})
