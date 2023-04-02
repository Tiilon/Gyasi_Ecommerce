from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from main_site.models import Cart, ProductCategoryModel,ProductModel,ProductImageModel, TicketModel
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date, datetime, timedelta
from django.db.models import Count

class DashboardView(LoginRequiredMixin,View):
    login_url = '/user/admin-login'
    today = date.today()
    currentWeek = date(today.year, today.month, today.day).strftime('%V')
    # for first_day for previous week it will be {int(currentWeek)-1}-1
    first_day_currentWeek= datetime.strptime(f"{today.year}-W{int(currentWeek)}-1", "%Y-W%W-%w").date()
    last_day_currentWeek = first_day_currentWeek + timedelta(days=6.9)
    
    first_day_previousWeek= datetime.strptime(f"{today.year}-W{int(currentWeek)-1}-1", "%Y-W%W-%w").date()
    last_day_previousWeek = first_day_previousWeek + timedelta(days=6.9)
    
    def get(self, request):
        template_name = "management/dashboard.html"

        #today's sales
        tickets = TicketModel.objects.filter(created_at=self.today) #get tickets for today
        ticket_today_sales = sum(ticket.product.ticket_price for ticket in tickets) #pyright:ignore

        #total sales
        tickets = TicketModel.objects.all() #get tickets for today
        ticket_total_sales = sum(ticket.product.ticket_price for ticket in tickets) #pyright:ignore

        #total products
        total_products = ProductModel.objects.all().count() #get total number of products

        # current weekly sales
        tickets = TicketModel.objects.filter(created_at__date__range=[self.first_day_currentWeek,self.last_day_currentWeek])
        current_week_ticket_sales = sum(ticket.product.ticket_price for ticket in tickets) #pyright:ignore

        #previous weekly sales
        tickets = TicketModel.objects.filter(created_at__date__range=[self.first_day_previousWeek,self.last_day_previousWeek])
        previous_week_ticket_sales = sum(ticket.product.ticket_price for ticket in tickets) #pyright:ignore

        # today's orders
        todays_orders = Cart.objects.filter(created_at__date=self.today).count() #get total number of orders

        # total orders
        total_orders = Cart.objects.all().count() #get total number of orders

        # total pending orders
        total_pending_orders = Cart.objects.filter(paid=False).count() #get total number of pending orders

        # total completed orders
        total_completed_orders = Cart.objects.filter(paid=True).count() #get total number of completed orders

        #current week orders
        current_weekly_orders_number = Cart.objects.filter(created_at__date__range=[self.first_day_currentWeek,self.last_day_currentWeek]).count()

        #previous week orders
        previous_weekly_orders_number = Cart.objects.filter(created_at__date__range=[self.first_day_previousWeek,self.last_day_previousWeek]).count()

        #best selling products
        best_selling_products = ProductModel.objects.annotate(count=Count('product_tickets')).order_by('count') #sales based on number of products sold

        best_selling_products_list = []
        for product in best_selling_products:

            # name of product
            product_name = product.name

            # name of product category
            product_category = product.category.name #pyright:ignore

            # owner of product
            product_owner = product.created_by.username #pyright:ignore

            #get number of product orders
            number_of_orders = product.cart_set.all().count() #pyright:ignore

            #get number of completed orders
            number_of_completed_orders = product.cart_set.filter(paid=True).count() #pyright:ignore
            completed_orders = product.cart_set.filter(paid=True) #pyright:ignore

            #get order percentage
            complete_order_percentage = (number_of_completed_orders/number_of_orders) * 100

            #get revenue by product
            product_revenue = sum(i.price for i in completed_orders)

            # revenue percentage of product
            product_revenue_percentage = (product_revenue/ticket_total_sales) * 100

            details = {
                'id':product.id, #pyright:ignore
                'name':product_name,
                'owner':product_owner,
                'category':product_category,
                'number_of_orders':number_of_orders,
                'number_of_completed_orders':number_of_completed_orders,
                'complete_order_percentage':complete_order_percentage,
                'revenue':product_revenue,
                'revenue_percentage':product_revenue_percentage,
            }
            best_selling_products_list.append(details)

        context = {
            'todays_sales': ticket_today_sales,
            'total_sales': ticket_total_sales,
            'total_products': total_products,
            'todays_orders': todays_orders,
            'total_orders': total_orders,
            'current_week_ticket_sales': current_week_ticket_sales,
            'previous_week_ticket_sales': previous_week_ticket_sales,
            'current_weekly_orders_number': current_weekly_orders_number,
            'previous_weekly_orders_number': previous_weekly_orders_number,
            'best_selling_products': best_selling_products_list,
            'total_pending_orders': total_pending_orders,
            'total_completed_orders': total_completed_orders,
        }

        return render(request, template_name, context)


class CategoryView(LoginRequiredMixin,View):
    def get(self, request):
        template_name = "management/categories.html"
        categories = ProductCategoryModel.objects.all()
        context = {'categories':categories}

        return render(request, template_name, context)
    
    def post(self, request):
        name = request.POST.get('cart_name')
        image = request.FILES.get('edit-cart-image')
        new_cart = ProductCategoryModel.objects.create(
            name = name,
            cart_sm_image = image,
            created_by=request.user
        )
        message = "success" if new_cart else ''
        return JsonResponse({'message': message})
    
@login_required
def get_categories(request):
    categories = ProductCategoryModel.objects.all()
    message = 'success'
    cart_list = []
    for cart in categories:
        details = {
            'id': cart.id, # pyright: ignore
            'name': cart.name,
            'created_by': cart.created_by.email, # pyright: ignore
            'cart_class': 'warning' if cart.status == 1 else 'success',
            'cart_txt': "<i title='Deactivate' class='far far fa-times-circle'></i>" if cart.status == 1 else "<i title='Activate' class='far fa-check-circle'></i>",
        }
        cart_list.append(details)
    return JsonResponse({'message': message, 'data': cart_list})

@login_required
def change_cart_status(request, cart_id):
    category = ProductCategoryModel.objects.get(id=cart_id)
    category.status = category.status != True
    category.save()
    return JsonResponse({'message': 'success'})

@login_required
def get_cart_details(request, cart_id):
    cart = ProductCategoryModel.objects.get(id=cart_id)
    details = {
        'id': cart.id, # pyright: ignore
        'name': cart.name,
        'image': cart.cart_sm_image.url if cart.cart_sm_image else '',
        'created_by': cart.created_by.email, # pyright: ignore
    }
    return JsonResponse({'message': 'success', 'details': details})

@login_required
def update_cart(request, cart_id):
    cart = ProductCategoryModel.objects.get(id=cart_id)
    name = request.POST.get('edit-cart-name')
    image = request.FILES.get('edit-cart-image')
    old_image = cart.cart_sm_image
    cart.name = name
    cart.cart_sm_image = image or old_image
    cart.save()
    return JsonResponse({'message': 'success'})
    
@login_required
def delete_cart(request, cart_id):
    category = ProductCategoryModel.objects.get(id=cart_id)
    category.delete()
    return JsonResponse({'message': 'success'})

class ProductListView(LoginRequiredMixin,ListView):
    model = ProductModel
    paginate_by = 6 # number of posts will load
    context_object_name = 'products'
    template_name = 'management/products.html'
    ordering = ['-created_at']
    
    def get_context_data(self,**kwargs):
        context = super(ProductListView,self).get_context_data(**kwargs)
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
                'images': images,
                'ticket_price': p.ticket_price,
                'status': p.status
            }
            product_list.append(details)
        context['products'] = product_list
        return context


@login_required # pyright: ignore
def create_product(request):
    if request.method == "POST":
        images = request.FILES.getlist('product_images')
        category = ProductCategoryModel.objects.get(id=request.POST.get('cart_id'))
        name= request.POST.get('name')
        ticket_price = request.POST.get('ticket_price')
        actual_price = request.POST.get('actual_price')
        description = request.POST.get('p_description')
        
        new_product = ProductModel.objects.create(
            category=category,
            name=name,
            ticket_price=ticket_price,
            actual_price=actual_price,
            description=description,
            status = True,
            created_by=request.user
        )
        
        for image in images:
            ProductImageModel.objects.create(
                product = new_product,
                image=image,
                product_admin_size=image,
                resized_image=image
            )
        return JsonResponse({'message': 'success'})


@login_required # pyright: ignore
def update_product(request,product_id):
    if request.method == "POST":
        images = request.FILES.getlist('p_images')
        product = ProductModel.objects.get(id=product_id)
        name= request.POST.get('p_name')
        ticket_price = request.POST.get('p_ticket')
        status = request.POST.get('p_status')
        description = request.POST.get('p_description')
        product.name = name
        product.ticket_price = ticket_price
        product.status = status
        product.description = description
        product.save()
        
        if images:
            for image in images:
                ProductImageModel.objects.create(
                    product = product,
                    image=image,
                    product_admin_size=image,
                    resized_image=image
                )
        return JsonResponse({'message': 'success'})
    
@login_required
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
        'images': [{'id':image.id,'url':image.product_admin_size.url} for image in images] #pyright: ignore
    }
    return render(request,'management/product_details.html',context)

@login_required      
def delete_product(request, product_id):
    product = ProductModel.objects.get(id=product_id)
    product.delete()
    return JsonResponse({'message': 'success'})

@login_required      
def delete_product_image(request, image_id):
    product_image = ProductImageModel.objects.get(id=image_id)
    product_image.delete()
    return JsonResponse({'message': 'success'})

def payment_page(request):
    return render(request,'management/payments.html')


@login_required
def get_tickets(request):
    tickets = TicketModel.objects.all()
    message = 'success'
    sales = []
    for sale in tickets:
        details = {
            'id': sale.id, # pyright: ignore
            'date': sale.created_at.date(),
            'owner': sale.user.email,
            'product': sale.product.name, # pyright: ignore
            'product_owner': sale.product.created_by.email, # pyright: ignore
            'ticket_status': 'Completed' if sale.status == 1 else 'Pending',
            'ticket_class': 'success' if sale.status == 1 else 'warning',
        }
        sales.append(details)
    return JsonResponse({'message': message, 'data': sales})