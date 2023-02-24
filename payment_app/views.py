import random
from django.shortcuts import get_object_or_404, redirect, render
from base.utils import send_winner_email

from main_site.models import Cart, TicketModel
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
    if not (verified := payment.verify_payment()):
        return JsonResponse({"message": "failed"})
    cart_items = Cart.objects.filter(user=request.user, paid=False)
    for item in cart_items:
        for i in range(item.quantity):
            new_ticket = TicketModel.objects.create(
                user = item.user,
                product = item.product,
            )
            number_of_tickets = item.product.number_of_tickets() #pyright:ignore
            product_tickets = item.product.product_tickets.filter(status=False).order_by("created_at")[:10] #pyright:ignore
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
        if not item.paid:
            item.paid = True
            item.payment_id = payment #pyright:ignore
            item.save()
    return JsonResponse({"message": "success"})
