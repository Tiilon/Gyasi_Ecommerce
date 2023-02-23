import contextlib
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from main_site.models import Cart, ProductCategoryModel, ProductImageModel, ProductModel
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.conf import settings
from django.core.mail import send_mail

class AboutUs(View):
    def get(self, request):
        template_name = "aboutus.html"
        context = {}
        return render(request, template_name, context)


# Api to search for image
def search_product(request):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'data': "Wrong request type"})
    products=[]
    input_product = request.POST.get('product')
    with contextlib.suppress(ProductModel.DoesNotExist):
        products = ProductModel.objects.filter(name__icontains=input_product)
    if len(input_product) > 0 and len(products) > 0:
        data = []
        for b in products:
            item = {
                'name': b.name,
            }
            data.append(item)
        res = data
    else:
        res = "No Suggestions keyword..."
    return JsonResponse({'data': res})

class ProductCategoryView(View):
    def get(self, request, cart_id):
        template_name = "public/category.html"
        category = ProductCategoryModel.objects.get(id=cart_id)
        context = {"category": category}

        return render(request, template_name, context)

    def post(self, request):
        name = request.POST.get("name")
        ProductCategoryModel.objects.create(name=name, created_by=request.user)
        return JsonResponse({"message": "success"})
    
class ProductView(ListView):
    model = ProductModel
    paginate_by = 12 # number of posts will load
    context_object_name = 'products'
    template_name = "public/items.html"

    ordering = ['-created_at']
    
    # def get(self, *args, **kwargs):
    #     send_mail('Testing','This is to test mail', 'tiilon42@gmail.com',['rigaji3511@mirtox.com'],fail_silently=False)
    
    def get_context_data(self,**kwargs):
        context = super(ProductView,self).get_context_data(**kwargs)
        product_list = []
        products = None
        if self.kwargs.get('cart_id'):
            category = ProductCategoryModel.objects.get(id=self.kwargs.get('cart_id'))
            products = ProductModel.objects.filter(category=category).order_by('-created_at')
            context['category']=category
        else:
            products = ProductModel.objects.all().order_by('-created_at')
        for p in products:
            images = ProductImageModel.objects.filter(product=p)
            details={
                'id': p.id, #pyright: ignore
                'cart_id': p.category.id, #pyright: ignore
                'name': p.name,
                'category': p.category.name,# pyright: ignore
                'image': images[0].image.url if images else '',
                'images': [{'id': image.id, 'url': image.image.url} for image in images],# pyright: ignore
                'ticket_price': p.ticket_price,
                'status': p.status
            }
            product_list.append(details)
        context['products'] = product_list
        return context
    

    def post(self, request, cart_id):
        name = request.POST.get("name")
        price = request.POST.get("price")
        category = get_object_or_404(ProductCategoryModel, pk=cart_id)
        image = request.File.get("image")
        ProductModel.objects.create(
            category=category,
            name=name,
            product_image=image,
            cart_sm_image=image,
            ticket_price=price,
            created_by=request.user,
        )
        return JsonResponse({"message": "success"})

def get_product_by_status(request, status, cart_id=None):
    product_list = []
    products = []
    
    if status == "all":
        if cart_id:
            cart = ProductCategoryModel.objects.get(id=cart_id)
            products = ProductModel.objects.filter(category=cart)
        else:
            products = ProductModel.objects.all()
    
    if status == "active":
        if cart_id:
            cart = ProductCategoryModel.objects.get(id=cart_id)
            products = ProductModel.objects.filter(category = cart,status=True)
        else:
            products = ProductModel.objects.filter(status=True)
            
    if status == "inactive":
        if cart_id:
            cart = ProductCategoryModel.objects.get(id=cart_id)
            products = ProductModel.objects.filter(category = cart,status=False)
        else:
            products = ProductModel.objects.filter(status=False)
            
    if status == "lowest":
        if cart_id:
            cart = ProductCategoryModel.objects.get(id=cart_id)
            products = ProductModel.objects.filter(category=cart).order_by("ticket_price")
        else:
            products = ProductModel.objects.all().order_by("ticket_price")
    
    if status == "highest":
        if cart_id:
            cart = ProductCategoryModel.objects.get(id=cart_id)
            products = ProductModel.objects.filter(category=cart).order_by("-ticket_price")
        else:
            products = ProductModel.objects.all().order_by("-ticket_price")
       
    for p in products:
        images = ProductImageModel.objects.filter(product=p)
        details={
            'id': p.id, #pyright: ignore
            'cart_id': p.category.id, #pyright: ignore
            'name': p.name,
            'category': p.category.name,# pyright: ignore
            'image': images[0].image.url if images else '',
            'images': [{'id': image.id, 'url': image.image.url} for image in images],# pyright: ignore
            'ticket_price': p.ticket_price,
            'status': p.status
        }
        product_list.append(details)
    return JsonResponse({"message": "success", "data": product_list})
        
# @login_required
def get_product_details(request, product_id):
    product = ProductModel.objects.get(id=product_id)
    images = ProductImageModel.objects.filter(product=product)
    context = {
        'id': product.id, #pyright:ignore
        'name': product.name,
        'status': product.status,
        'description': product.description,
        'category': product.category.name, #pyright: ignore
        'ticket_price': product.ticket_price,
        'images': [{'id':image.id,'url':image.image.url} for image in images] #pyright: ignore
    }
    return JsonResponse({"message": "success", "data": context})
    
class CartView(View):
    def get(self, request):
        template_name = "public/cart.html"
        cart_items = Cart.objects.filter(user = request.user) 
        cart_list = []
        total_payable = 0
        for item in cart_items:
            p_image = ProductImageModel.objects.filter(product=item.product)
            image = p_image[0].image.url
            details={
                "id": item.id, #pyright: ignore
                "product": item.product.name, #pyright: ignore
                "ticket": item.product.ticket_price, #pyright: ignore
                "quantity": item.quantity,
                "price": item.price,
                "image": image,
            }
            cart_list.append(details)
            total_payable += item.price #pyright: ignore
        context = {
            'cart_items': cart_list,
            'total_payable': total_payable,
            'cart_count': cart_items.count(),
        }
        return render(request, template_name, context)

def delete_cart(request, cart_id):
    cart_item = Cart.objects.get(id=cart_id)
    cart_item.delete()
    return JsonResponse({"message": "success"})
    
def get_cart_items(request):
    cart_items = Cart.objects.filter(user__id = request.user.id) or []
    cart_list = []
    total_payable = 0
    for item in cart_items:
        details={
            "product": item.product.name, #pyright: ignore
            "ticket": item.product.ticket_price, #pyright: ignore
            "quantity": item.quantity,
            "price": item.price,
        }
        cart_list.append(details)
        total_payable += item.price #pyright: ignore
    return JsonResponse({"message": "success", "data": cart_list, "total_payable": total_payable, "cart_number": len(cart_list)})


def add_cart_item(request, product_id):
    item, created = Cart.objects.get_or_create(user=request.user, product_id=product_id)
    quantity = request.POST.get('quantity')
    price = request.POST.get('price')
    
    item.quantity = quantity
    item.price = price 
    item.save()
    
    return JsonResponse({"message": "success"})
    

class CheckOutView(View):
    def get(self, request):
        template_name = "public/checkout.html"
        cart_items = Cart.objects.filter(user = request.user)
        cart_list = []
        total_payable = 0
        for item in cart_items:
            p_image = ProductImageModel.objects.filter(product=item.product)
            image = p_image[0].image.url
            details={
                "id": item.id, #pyright: ignore
                "product": item.product.name, #pyright: ignore
                "ticket": item.product.ticket_price, #pyright: ignore
                "quantity": item.quantity,
                "price": item.price,
                "image": image,
            }
            cart_list.append(details)
            total_payable += item.price #pyright: ignore
        context = {
            'cart_items': cart_list,
            'total_payable': total_payable,
            'cart_count': cart_items.count(),
            'public_key':settings.PAYSTACK_PUBLIC_KEY
        }
        return render(request, template_name, context)
        