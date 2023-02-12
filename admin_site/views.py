from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.core.paginator import Paginator
from main_site.models import ProductCategoryModel,ProductModel,ProductImageModel
from utils import tokenizer
from django.views.generic.list import ListView

class DashboardView(View):
    def get(self, request):
        template_name = "admin/dashboard.html"
        # products = ProductModel.objects.all()
        context = {}

        return render(request, template_name, context)


class CategoryView(View):
    def get(self, request):
        template_name = "admin/categories.html"
        categories = ProductCategoryModel.objects.all()
        context = {'categories':categories}

        return render(request, template_name, context)
    
    def post(self, request):
        name = request.POST.get('cart_name')
        message = ''
        new_cart = ProductCategoryModel.objects.create(
            name = name,
            created_by=request.user
        )
        if new_cart:
            message = "success"
        return JsonResponse({'message': message})
    

def get_categories(request):
    categories = ProductCategoryModel.objects.all()
    message = 'success'
    cart_list = []
    for cart in categories:
        details = {
            'id': cart.id,
            'name': cart.name,
            'created_by': cart.created_by.email,
            'cart_class': 'warning' if cart.status == 1 else 'success',
            'cart_txt': 'Deactivate' if cart.status == 1 else 'Activate',
        }
        cart_list.append(details)
    return JsonResponse({'message': message, 'data': cart_list})

def change_cart_status(request, cart_id):
    category = ProductCategoryModel.objects.get(id=cart_id)
    if category.status == True:
        category.status = False
        category.save()
        print(category.status)
        return JsonResponse({'message': 'success'})
    else:
        category.status = True
        category.save()
        return JsonResponse({'message': 'success'})
    return JsonResponse({'message': 'failed'})


def delete_cart(request, cart_id):
    category = ProductCategoryModel.objects.get(id=cart_id)
    category.delete()
    print(category)
    # category.save()
    return JsonResponse({'message': 'success'})

class ProductListView(ListView):
    model = ProductModel
    paginate_by = 6 # number of posts will load
    context_object_name = 'products'
    template_name = 'admin/products.html'
    ordering = ['-created_at']
    
    def get_context_data(self,**kwargs):
        context = super(ProductListView,self).get_context_data(**kwargs)
        product_list = []
        products = None
        if self.kwargs.get('cart_id'):
            category = ProductCategoryModel.objects.get(id=self.kwargs.get('cart_id'))
            products = ProductModel.objects.filter(category=category).order_by('-created_at')
            
        else:
            products = ProductModel.objects.all().order_by('-created_at')
        for p in products:
            images = ProductImageModel.objects.filter(product=p)
            details={
                'name': p.name,
                'category': p.category.name,
                'image': images[0].image.url,
                'ticket_price': p.ticket_price,
                'status': p.status
            }
            product_list.append(details)
        context['products'] = product_list
        return context
    
def create_product(request):
    if request.method == "POST":
        images = request.FILES.getlist('product_images')
        category = ProductCategoryModel.objects.get(id=request.POST.get('cart_id'))
        name= request.POST.get('name')
        ticket_price = request.POST.get('ticket_price')
        
        new_product = ProductModel.objects.create(
            category=category,
            name=name,
            ticket_price=ticket_price,
        )
        
        for image in images:
            ProductImageModel.objects.create(
                product = new_product,
                image=image,
                resized_image=image
            )
        return JsonResponse({'message': 'success'})
        