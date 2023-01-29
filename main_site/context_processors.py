from main_site.models import ProductCategoryModel

def all_categories(request):    
    all_categories = ProductCategoryModel.objects.all()  
    return {'all_categories': all_categories}