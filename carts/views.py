from multiprocessing import context
# import re
from django.shortcuts import get_object_or_404, render, redirect
from store.models import Product, Variation
from . models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required




# ========>   Getting the session from here   <========


def _cart_id(request):
    # ===> we are creating a new session
    cart = request.session.session_key
    if not cart:
    # ===> if there is no session, a new seesion will be created
        cart = request.session.create()
    # ===> this will return the cart id
    return cart




# ========>   Add the product inside the cart   <========
# ===> the cart item is getting stored base on the cart id or session id.
def add_cart(request, product_id):
    current_user = request.user
    # ===> getting the id of each products
    # ==> we are getting the product from the pro id
    product = Product.objects.get(id=product_id)
    # ===> if the user is authenticated
    if current_user.is_authenticated:
    # ===> getting the id of each products
    # ==> we are getting the product from the pro id
        product_variation = []
        if request.method == 'POST':
            
            # ===> we want to make sure that in the future any variation can come in like brand, author and so on 
            # ===> we want to loop through whatever that is coming from the POST request
            for item in request.POST:
                # ===> we want to collect just anything coming in as key and value
                # ===> item is the iterator
                key = item
                # ===> values hold the request
                value = request.POST[key]
                
                # ===> we are checking if the key and value coming from the request.POST is matching with the models value, which means variation values that we have created in the database which is the admin panel.
                

                try:
                    # ===> 'i__exact' will ignore if the key or value is capital letter or small letter 
                    # ===> we also want to get the specific variation for a particular product
                    variation = Variation.objects.get(product = product, variation_category__iexact = key, variation_value__iexact = value)
                    # ===> appending the variation here
                    product_variation.append(variation)
                except:
                    pass
            
        # # ===> the 'color' is coming from the select drop-down in the product_detail.html
        #     color = request.POST['color']
        #     size = request.POST['size']





    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ===> we want to be able to group each cart items togethere which means that when a product with the same variation is added we want to group them together 
    # ===> we also wants to store each variations for each products 
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------







        # ===> we are checking if the cart item exist
        # ===> this will return a true of false value
        # ===> we want to put the product inside the cart
        # ===> when we put the product inside the cart the product becomes cart item
        # ===> in one cart there can be multiple products or there can be multiple cart items
        # ===> we want to combine the product and the cart so that we get the cart item
        is_cart_item_exists = CartItem.objects.filter(product = product, user=current_user).exists()
        if is_cart_item_exists:
            # ===> 
            # ===> the product we are talking about is the 'product = product,' we collect in the add_cart function
            # ===> 'cart = cart' this will bring us the cart items
            # ===> when the same product is added with a different variation, we want to filter it and store them inside the cart item
            # ===> the cart item is comming from the database
            # ===> this will return the cart item object
            cart_item = CartItem.objects.filter(product = product, user=current_user)
            # ===> we need existing variations and current variations
            # ===> we also need the item id
            # ===> if the current variation is inside the existing variations then increase the quantity of cart
            # ===> getting the existing variation list from the database.
            ex_var_list = []
            id  = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
                            
            # ===> we are increasing the cart item if the variation of the cart item that we want to add is already inside the cart item in the  database.
            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product = product, id = item_id)
                item.quantity += 1
                item.save()
                
            else:
                # ===> if is not in the database
                item = CartItem.objects.create(product = product, quantity = 1, user=current_user)
                # ===> we want to check if the product variation is empty or not
                # ===> if it is empty we are going to update it quantity and if it is not empty we add the items inside the database
                if len(product_variation) > 0:
                    item.variations.clear()
                    # ===> '*product_variation' will make sure it add the product variation
                    item.variations.add(*product_variation)
                item.save()
            # ===> if the cart item doesNotExist
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user=current_user 
            )
            
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()        
        # ===> redirect the user to the cart page again
        return redirect('cart')
    # ===> if the user is not authenticated
    else:
        # ===> we want to make a list of objects because, we can add as many products as possible, i.e the product with the variation
        product_variation = []
        if request.method == 'POST':
            
            # ===> we want to make sure that in the future any variation can come in like brand, author and so on 
            # ===> we want to loop through whatever that is coming from the POST request
            for item in request.POST:
                # ===> we want to collect just anything coming in as key and value
                # ===> item is the iterator
                key = item
                # ===> values hold the request
                value = request.POST[key]
                
                # ===> we are checking if the key and value coming from the request.POST is matching with the models value, which means variation values that we have created in the database which is the admin panel.
                

                try:
                    # ===> 'i__exact' will ignore if the key or value is capital letter or small letter 
                    # ===> we also want to get the specific variation for a particular product
                    variation = Variation.objects.get(product = product, variation_category__iexact = key, variation_value__iexact = value)
                    # ===> appending the variation here
                    product_variation.append(variation)
                except:
                    pass
            
        # # ===> the 'color' is coming from the select drop-down in the product_detail.html
        #     color = request.POST['color']
        #     size = request.POST['size']
            #     
        
        # ===> 
        try:
            
            
            # ===> we are getting the cart by the cart id
            # ===> we are bring the cart id from the session
            # ===> And store the cart id in the database
            # ===> getting the cart using the 'cart_id' that is present in the session
            # ===> 'cart id' should be equal to the session id
            cart = Cart.objects.get(cart_id=_cart_id(request))  
        except Cart.DoesNotExist:
            # ===> if the cart does not exist
            # ===> then create a new cart
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()







    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ===> we want to be able to group each cart items togethere which means that when a product with the same variation is added we want to group them together 
    # ===> we also wants to store each variations for each products 
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------







        # ===> we are checking if the cart item exist
        # ===> this will return a true of false value
        # ===> we want to put the product inside the cart
        # ===> when we put the product inside the cart the product becomes cart item
        # ===> in one cart there can be multiple products or there can be multiple cart items
        # ===> we want to combine the product and the cart so that we get the cart item
        is_cart_item_exists = CartItem.objects.filter(product = product, cart = cart).exists()
        if is_cart_item_exists:
            # ===> 
            # ===> the product we are talking about is the 'product = product,' we collect in the add_cart function
            # ===> 'cart = cart' this will bring us the cart items
            # ===> when the same product is added with a different variation, we want to filter it and store them inside the cart item
            # ===> the cart item is comming from the database
            # ===> this will return the cart item object
            cart_item = CartItem.objects.filter(product = product, cart = cart)
            # ===> we need existing variations and current variations
            # ===> we also need the item id
            # ===> if the current variation is inside the existing variations then increase the quantity of cart
            # ===> getting the existing variation list from the database.
            ex_var_list = []
            id  = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
                
            print(ex_var_list)
            
            # ===> we are increasing the cart item if the variation of the cart item that we want to add is already inside the cart item in the  database.
            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product = product, id = item_id)
                item.quantity += 1
                item.save()
                
            else:
                # ===> if is not in the database
                item = CartItem.objects.create(product = product, quantity = 1, cart = cart)
                # ===> we want to check if the product variation is empty or not
                # ===> if it is empty we are going to update it quantity and if it is not empty we add the items inside the database
                if len(product_variation) > 0:
                    item.variations.clear()
                    # ===> '*product_variation' will make sure it add the product variation
                    item.variations.add(*product_variation)
                item.save()
            # ===> if the cart item doesNotExist
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()        
        # ===> redirect the user to the cart page again
        return redirect('cart')

        
        
        
        
# ========>  Decrease a particular product from the cart items list   <========
def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product = product, user = request.user, id = cart_item_id)
        else:
            # ===> this code will run when we are not logged in.
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product = product, cart = cart, id = cart_item_id)
        # ===> if cart items quantity is greater than one
        if cart_item.quantity > 1:
            # ===> the cart item should be delete
            # ===> it will decrement the quantity
            cart_item.quantity -= 1
            cart_item.save()
        else:
            # ===> delete the cart item
            cart_item.delete()
    except:
        pass
    return redirect('cart')
    



# ========> Remove a particular product from the cart items list   <========
def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product = product, user = request.user, id=cart_item_id)

    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product = product, cart = cart, id=cart_item_id)
    # ===> when we click on the remove button it should remove
    cart_item.delete()
    return redirect('cart')







def cart(request, total = 0, quantity= 0, cart_items = None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user, is_active = True)
        else:
            # cart_items = 0
            # ===> these will bring all the cart items
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
            # ===> if the object does not exist it will ignore
    except ObjectDoesNotExist:
        pass
    
    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)





# ========> Checkout View   <========
@ login_required(login_url='login')
# @login_required
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user, is_active = True)
        else:
            # cart_items = 0
            # ===> these will bring all the cart items
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
            # ===> if the object does not exist it will ignore
    except ObjectDoesNotExist:
        pass
    
    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)