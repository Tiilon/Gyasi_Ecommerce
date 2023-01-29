from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.http import JsonResponse

from main_site.models import ProductCategoryModel, ProductModel


class AboutUs(View):
    def get(self, request):
        template_name = "aboutus.html"
        context = {}
        return render(request, template_name, context)


class HomeView(View):
    def get(self, request):
        template_name = "public/home.html"
        products = ProductModel.objects.all()
        context = {"products":products}

        return render(request, template_name, context)


# Api to search for image
def search_product(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        products=[]
        input_product = request.POST.get('product')
        try:
            products = ProductModel.objects.filter(name__icontains=input_product)
        except ProductModel.DoesNotExist:
            pass
        
        if len(input_product) > 0 and len(products) > 0:
            data = []
            for b in products:
                item = {
                    'name': b.name,
                }
                data.append(item)
            res = data
            print(res)
        else:
            res = "No Suggestions keyword..."
        return JsonResponse({'data': res})
    return JsonResponse({'data': "Wrong request type"})

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


class ProductView(View):
    def get(self, request):
        template_name = "public/items.html"
        products = ProductModel.objects.all()
        context = {"products": products}

        return render(request, template_name, context)

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


class CartView(View):
    def get(self, request):
        template_name = "admin/cart.html"
        context = {}

        return render(request, template_name, context)


class CheckoutView(View):
    def get(self, request):
        template_name = "admin/checkout.html"
        context = {}

        return render(request, template_name, context)
