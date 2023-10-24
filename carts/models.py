# from itertools import product
# from pyexpat import model
# from tkinter import CASCADE
from django.db import models
from store.models import Product, Variation
from accounts.models import Account







# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    
    
    def __str__(self):
        return self.cart_id
    

class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product     = models.ForeignKey(Product, on_delete=models.CASCADE)
    # ===> we also want to store the variation inside the cart
    # ===> we are using 'ManyToManyField' because many products can have same variations
    
    variations = models.ManyToManyField(Variation, blank=True)
    cart        = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity    = models.IntegerField()
    is_active   = models.BooleanField(default=True)
    
    
    def sub_total(self):
        # ===> 'self' means that we are refering to the CartItem <==> model, 
        # ===> 
        return self.product.price * self.quantity


    def __unicode__(self):
        return self.product