from django.contrib import admin
from .models import Payment, Order, OrderProduct
# Register your models here.


# ===> ['TabularInline']  When we need to use TabulerInline on Django Admin, the admin template create a "title" for the field... it's not the verbose_name... verbose_name is set like a Group.. "Blue" line before TabularInline... after this line, we have a table title... that's my problem... how can I change these "table title" on TabularInline?
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ['payment', 'user', 'product', 'quantity', 'product_price', 'ordered']
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'email', 'city', 'order_total', 'tax', 'status', 'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_page = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_per_page = 20
    inlines = [OrderProductInline]

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
