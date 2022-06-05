# from ast import Or
# import imp
# from typing_extensions import OrderedDict
from django.shortcuts import render, redirect
from carts.models import CartItem
from .forms import OrderForm
import datetime

from .models import Order, Payment, OrderProduct

import json
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

from django.core.mail import EmailMessage

from django.template.loader import render_to_string

# Create your views here.



# =====> payments views <=====
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number = body['orderID'])
    # ===> Store transaction details inside payment Model;
    
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    
    payment.save()
    
    order.payment = payment
    # ===> when we are done with the payment we need to set the users orders to True.
    order.is_ordered = True
    order.save() 
    
    # ===> when we move the cart items to the order product table we want to, then we also hv to reduce the quantity of sold products
    # ===> Move cart_items to Order Product table
    
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        # ===> by this time our payment is true
        orderproduct.order = True
        orderproduct.save()
        
        
        cart_item = CartItem.objects.get(id=item.id)
        # ===> from this ['cart_item'] we want to take the ['product_variation']
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()
     
    
    
    # ===> Reduce quantity of the sold products
    # ===> because once the product is sold the it has to be reduced in the database for the remaining items left
    # ===> Clear the cart
    
    CartItem.objects.filter(user=request.user).delete()
    
    # ===> then send Order recieved email to the customer
    mail_subject = 'Thank you for your order!'
            # ===> we want to put the content we want to send in the email, i.e the template
            # ===> in the message we are taking the user object
    message = render_to_string('orders/order_recieved_email.html', {
        # ===> this is the user object,
        # ===> in the verification email we want to tell the user that how about their account user.firstname.
        'user' : request.user,
        'order': order,
    })
    to_email = request.user.email
    # ===> 
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()
    
    # ===> Send order number and transaction id back to the sendData method Via JsonResponse ['Json data sender in the frontend'] we will recive it by data
    # ===> we are sending the data via the ['Json'] response., cos once we send the ['Json'] response from there we will be getting the data in the ['.then(response => response.json())
    # .then(data => console.log(data)):'] so that we will redirect the user to t he thank you page.
    
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)
    
    # ===> in the thank you page we will be having the list of product we bought and the transaction id and the we will also be getting the order number
    # return render(request, 'orders/payments.html')








# =====> place_order views <=====
def place_order(request,  total = 0, quantity= 0,):
    current_user = request.user
    
    # ===> if the cart count is less than or equal to zero. then redirect back to the store.
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax
    if request.method == 'POST':
        form  = OrderForm(request.POST)
        if form.is_valid():
            # ===> if the form is valid store all the Billing informations.
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            # ===> ['REMOTE_ADDR'] will bring the user ip address.
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            
            # =====> generate order number <=====
            # ===> after saving this data it will generate the ['primarykey'] or id.
            # ===> we are generating the order id.
            # ===> we are obtaining the ['current month', 'current date' and 'current year']
            
            
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20220401
            # ===> we are getting the data id and it will be unique.
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            # ===> to get the billing informations.
            order = Order.objects.get(user=current_user, is_ordered = False, order_number = order_number)

            context = {
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax, 
                'grand_total' : grand_total
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        # ===> show the other product and filter it by the order id
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        
        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
        
        
        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order' : order,
            'ordered_products' : ordered_products,
            'order_number' : order.order_number,
            'transID' : payment.payment_id,
            'subtotal' : subtotal
        }
        return render(request, 'orders/order_complete.html', context)  
    # ===> ['window.location.href = redirect_url + '?order_number='+data.order_number+'&payment_id='+data.transID; '] will redirect the user after success 
    # ===> and also get the user details and order product
    except (Payment.DoesNotExist, Order.DoesNotExist):
        # ===> when someone put a wrong id here they will be redirected to the home page
        return redirect('home')
            

            
            