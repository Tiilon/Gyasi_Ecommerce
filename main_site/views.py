from django.shortcuts import redirect, render, get_object_or_404
from django.views import View


class AboutUs(View):
    def get(self, request):
        template_name = "aboutus.html"
        context = {}
        return render(request, template_name, context)


class HomeView(View):
    def get(self, request):
        template_name = "admin/home.html"
        context = {}

        return render(request, template_name, context)


class CategoryView(View):
    def get(self, request):
        template_name = "admin/category.html"
        context = {}

        return render(request, template_name, context)
    
class ItemsView(View):
    def get(self, request):
        template_name = "admin/items.html"
        context = {}

        return render(request, template_name, context)
    
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
