from django.contrib import admin
from .models import Cart, CartItem
# Register your models here.


# how we want the cart items to display in the admin panel
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added')


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'is_active')




admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)

