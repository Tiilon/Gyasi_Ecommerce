from django.contrib import admin

from main_site.models import Cart, ProductImageModel, ProductModel, ProductCategoryModel, TicketModel

# Register your models here.
admin.site.register(ProductCategoryModel)
admin.site.register(ProductModel)
admin.site.register(Cart)
admin.site.register(ProductImageModel)
admin.site.register(TicketModel)