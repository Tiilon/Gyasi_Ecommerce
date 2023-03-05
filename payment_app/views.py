from django.shortcuts import get_object_or_404
# from base.utils import send_payment_receipt, send_winner_email
from main_site.models import Cart
from .models import Payment
from django.http import JsonResponse


# To use celery in sending email
from main_site.tasks import send_payment_receipt, create_ticket

def initiate_payment(request):
    if request.method == "POST":
        amount = request.POST.get('amount')
        email = request.POST.get('email')
        payment = Payment.objects.create(amount=amount, email=email)
        return JsonResponse({"message": "success", 'data': payment.reference})

def verify_payment(request, ref):
    payment = get_object_or_404(Payment, reference=ref)
    if not (verified := payment.verify_payment()):
        return JsonResponse({"message": "failed"})
    
    #use of tradtional payment without celery
    item_list=[]
    cart_items = Cart.objects.filter(user=request.user, paid=False)
    for item in cart_items:
        create_ticket.delay(item.quantity, item.user.id, item.product.id) # type: ignore
    #     for _ in range(item.quantity):
    #             new_ticket = TicketModel.objects.create(
    #                 user = item.user,
    #                 product = item.product,
    #             )
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
    send_payment_receipt.delay(request.user.email, item_list)  # type: ignore
    return JsonResponse({"message": "success"})
