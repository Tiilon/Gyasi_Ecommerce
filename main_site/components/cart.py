from django_unicorn.components import UnicornView, QuerySetType
from main_site.models import Cart


class CartView(UnicornView):
    cart_items: QuerySetType[Cart] = None #pyright:ignore
    user_id: int
    
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.user_id = kwargs.get('user') #pyright:ignore
        self.cart_items = Cart.objects.filter(user__id=self.user_id) #pyright:ignore
        
    