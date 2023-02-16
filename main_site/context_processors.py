from main_site.models import ProductCategoryModel, ProductModel
from django.db.models import Count

def selected_categories(request):
    cart_list = []
    all_categories = ProductCategoryModel.objects.all().annotate(product_count=Count('products')).order_by('-product_count')[:7]
    for cart in all_categories:
        products = ProductModel.objects.filter(category=cart)[:11]
        cart_details = {
            'name': cart.name,
            'products': [{'name':product.name, 'id':product.id} for product in products] #pyright:ignore
        }
        cart_list.append(cart_details)
    return {'all_categories': cart_list}

def all_categories(request):
    cart_list = []
    all_categories = ProductCategoryModel.objects.all().order_by('name')
    for cart in all_categories:
        products = ProductModel.objects.filter(category=cart)
        cart_details = {
            'id': cart.id,#pyright:ignore
            'name': cart.name,
            'products': [{'name':product.name, 'id':product.id} for product in products] #pyright:ignore
        }
        cart_list.append(cart_details)
    return {'total_categories': cart_list}