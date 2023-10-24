# import email
from email.message import EmailMessage
from multiprocessing import context
from re import U
from unicodedata import is_normalized
# import re
# from urllib import request
from django.shortcuts import render, redirect, get_object_or_404

# from boldcom import accounts
from .forms import RegistrationForm, UserForm, UserProfileForm 
from .models import Account, UserProfile
from orders.models import Order, OrderProduct
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.http import HttpResponse




# ========> Importing for email verification   <======== 
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


from django.core.mail import send_mail
from django.conf import settings



from carts.views import _cart_id
from carts.models import Cart, CartItem



import requests


# Create your views here.

# ========> Register View <========
def register(request):
    if request.method == 'POST':
        
        # ===> this will contain all the field value
        form = RegistrationForm(request.POST)
        # ===> if the form is valid
        if form.is_valid():
            

            # ===> firstly we are fetching all the fields from the request 'POST'
            # ===> when we use django forms we have to use the 'cleaned_data' to fetch the values from the request
            

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            

            # ===> we are creating the username base on the user email address 
            # ===> we want to take the some part from the email provided be the user
            

            username = email.split("@")[0]
            

            # ===> we want to create the user account
            # ===> the 'create_user' is from the django authentication model that we create in the model file
            

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()
            
            # ========> User activation <========
            # ===> we are getting the current site, beacuse we are using the localhost
            current_site = get_current_site(request)
            # ===> we are taking the mail subject
            mail_subject = 'Please activate your account'
            # ===> we want to put the content we want to send in the email, i.e the template
            # ===> in the message we are taking the user object
            message = render_to_string('accounts/account_verification_email.html', {
                # ===> this is the user object,
                # ===> in the verification email we want to tell the user that how about their account user.firstname.
                'user' : user,
                'domain' : current_site,
                # ===> we are encoding this 'user.pk'  with ' urlsafe_base64_encode' so that nobody can see the primary key.
                # ===> we are also encoding the user primary key
                # ===> when we are activating the account we will decode it.
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                # ===> this 'default_token_generator.make_token' is the libery it has make.token and check.token functions, 'make_token ' will create a token of the user, it will create a token for the user.
                # ===> we are generatiing the token of that user
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            # ===> 
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # ===> 'success' is the success message
            # messages.success(request, 'Thank you for registering with us we have sent you a verification on your email, please verify it.')
            # ===> we want to send the user to the login
            # ===> This is just for checking purpose to know if the user is coming from the registering form
            # ===> if the user is coming from the registering form he should register his account
            # ===> ' + email is the dynamic email coming from the user registration form
            # ===> This [('accounts/login/?command=verification=' + email)] will come to the browser url will we take the values there
            return redirect('/accounts/login/?command=verification=' + email)
    else:
        form = RegistrationForm()
    context = {
        'form' : form,
    }
    return render(request, 'accounts/register.html', context)





# ========> Login View <========
def login(request):
    if request.method == 'POST':
        # ===> from the login form, the name values.
        email = request.POST['email']
        password = request.POST['password']
        
        # * ===> will set the user so they can login
        user = auth.authenticate(email=email, password=password)
        
        if user is not None:
            try:
                # * ===> the ['_cart_id'] is from the carts app it is also a function in the view inside the app, we have to import it. 
                # ===> when we add to cart while we have logout we want have the same cart item when we log in.
                # ===> if there is something inside the cart while we have not logged in
                cart = Cart.objects.get(cart_id= _cart_id(request))
                # ===> we are just assigning the user to the cart item
                is_cart_item_exists = CartItem.objects.filter(cart = cart).exists()
                if is_cart_item_exists:
                    # * ===>  this cartitem will give us all the cart that are already assing for the cart id
                    cart_item = CartItem.objects.filter(cart=cart)
                    
                    # ===> we want to group the cart item for inside it variation when the user logs in
                    # ===> getting the product variation by the cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        # ===> we are making it ['list(variation))'] a list because by default it is a queryset
                        product_variation.append(list(variation))
                    
                    
                    # ===> get the cart item from the to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
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
                        
                        
                        # ===> if the cart item is common in the existing variation list
                        
                        
                        # product_variation = [1, 2, 3, 4, 5, 6, 7, 8]
                        # ex_var_list = [2, 5, 8, 6, 1]
                        
                        
                        
                        
                    # ===> to get the common product variation 
                    # ===> we are looping through the product_variation to find  if there is common variation inside the two list
                    for pr in product_variation:
                        if pr in ex_var_list:
                            # ===> ('pr') is the position where we find the common item.
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                            
                        else:
                            cart_item = CartItem.objects.filter(cart = cart)
                            for item in cart_item:
                                # ===> this is assigning the user to the cartitem
                                item.user = user
                                item.save()  
            except:
                pass  
            auth.login(request, user)
            messages.success(request, 'Your are now loggged in')
            # ===> THIS ['request.META.get('HTTP_REFERER')']  will grab the previous url from where you came,  you are coming from
            # ===> it wil store the url inside the ['url'] variable.
            url = request.META.get('HTTP_REFERER')
            try:
                # ['requests'] --> which is the request libery
                query = requests.utils.urlparse(url).query
                # ===> next=/cart/checkout/
                # ===> the ['x.split'] is spliting the ['='] sign 
                # ===> ['next'] is the key and ['cart/checkout'] as the value.
                params  = dict(x.split('=') for x in query.split('&'))
                # ===> we want to redirect the user to the value of the ['next']
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')


@login_required(login_url='login')
# ========> Logout View <========
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')


# ========> Activate View <========
def activate(request, uidb64, token):
    
    
    
    # * ===>   this ' urlsafe_base64_decode(uidb64).decode()' will decode the uidb,because we encoded it earlier, we are now decoding it.
    # ===> it will give us the primary key of the user.
    

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        
        # ===> this 'Account._default_manager.get(id=uid)' will return the user object
        
        user = Account._default_manager.get(id=uid)
        
        # ===> we are handling some errors
        # ===> if these or any of these error happens we are setting the user to none
        

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user  = None
        
        
    # ===> we are checking the token
    # ! ===>  if the error does not happen
    # ===> we
    # want to take out the user from the token  ' check_token()'
    # ===> default_token_generator will generate the token of the user
        
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()  # * Save the user after updating is_active
        
        messages.success(request, 'Congratulations! your account is activated.')
        return redirect('login')

    else:
        messages.error(request,'Invalid activation link.')
        return redirect('register')
    
    
    
    
    

# ========> Logout View <========
# ===> if you are not logged in you can't access the dashboard
@login_required(login_url='login')
def dashboard(request):
    # try:
    #     userprofile = UserProfile.objects.get(user=request.user)
    # except UserProfile.DoesNotExist:
    #     userprofile = None
    
    userprofile = UserProfile.objects.filter(user=request.user).first()
    
    # If userprofile doesn't exist, redirect to the home page
    if not userprofile:
        return redirect('home')
    # ===> we are taking the number of product the person has ordered
    # *[VALID✅] orders = Order.objects.order_by('-created_at').filter(user_id = request.user.id, is_ordered = True)
    orders = Order.objects.order_by('-created_at').filter(user=request.user, is_ordered=True)

    orders_count = orders.count()
    # return HttpResponse('adams', orders_count)
    
    userprofile = UserProfile.objects.get(user_id = request.user.id)
    # userprofile = get_object_or_404(UserProfile, user__id= request.user.id)
    # return HttpResponse('adams', userprofile)
    context = {
        'orders_count' : orders_count,
        'userprofile'  : userprofile,
        
    }
    return render(request, 'accounts/dashboard.html', context)



# Django 4.0 and higher
from django.utils.encoding import force_str
from accounts.tokens import account_activation_token
from django.core.mail import send_mail

# ========> forgotPassword View <========
def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']

        # ===> we are checking if the account exist or not.
        # ===> ['.filter('] will return an empty queryset if there are no users with the specified email address.
        users = Account.objects.filter(email=email)

        if users.exists():
            user = users.first()

            # Reset password email
            current_site = get_current_site(request)

            # ===> we are taking the mail subject
            mail_subject = 'Reset Your password'

            # ===> we want to put the content we want to send in the email, i.e the template
            # ===> in the message we are taking the user object
            message = render_to_string('accounts/reset_password_email.html', {
                'user' : user,
                'domain' : current_site.domain,
                # 'uid': urlsafe_base64_encode(force_str(user.pk)),
                # 'uid': urlsafe_base64_encode(user.pk.to_bytes(length=8, byteorder='big')),
                # * generating a unique identifier for the user, which will be used in the reset password link that is sent to the user's email address.
                # ! [NOTE] -> The urlsafe_base64_encode() function takes a string as input and returns a base64 encoded string that is safe to use in URLs. This is because the base64 encoding removes any characters that could be interpreted as special characters in URLs. However, the uid variable is a string, and the urlsafe_base64_encode() function expects a bytes-like object.
                'uid': urlsafe_base64_encode(str(user.pk).encode('utf-8')),
                'token' : default_token_generator.make_token(user),
            })

            to_email = email

            try:
                send_mail(mail_subject, message, from_email=settings.EMAIL_HOST_USER, recipient_list=[to_email])
            except Exception as e:
                messages.error(request, 'Failed to send password reset email: {}'.format(e))
                print(e)

            messages.success(request, 'Password reset email has been sent to your mail address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')

    return render(request, 'accounts/forgotPassword.html')








# ========> forgotPassword View That will send the reset password link to the user <========
# Django 4.0 and higher
from django.utils.encoding import force_str
def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        # uid = urlsafe_base64_decode(uidb64)
        # uid = force_text(urlsafe_base64_decode(uidb64))
        # ===> this 'Account._default_manager.get(id=uid)' will return the user object
        user = Account._default_manager.get(id=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExists):
        user  = None
        
        
    if user is not None and default_token_generator.check_token(user, token):
        # if user is not None and default_token_generator.check_token(user, token):
        # ===> we are saving the uid inside the session
        request.session['uid'] = uid
        messages.success(request, 'Please reset Your password')
        # 
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has expired')
        return redirect('login')
    
    
    
    
    
    
    
# ========> resetPassword View <========
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        
        if password == confirm_password:
            # ===> we are getting the uid from the session
            uid  = request.session.get('uid')
            
            user = Account.objects.get(pk=uid)
            # ===> we are setting the user to the password  from the request above, if you dont use ['set_password'] or just save your password inside the database the password will not the set and the user will not be able to login with the password that they intend to use, becasuse the ['set_password'] is a django built in function.
            # it will take the password and save it in a hashed format.
            user.set_password(password)
            user.save()
            messages.success = (request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password does not match')
            return redirect('resetPassword')
        # ===> if the request is not == 'POST'
    else:
        return render(request, 'accounts/resetPassword.html')


# =====> my_order views <=====
@login_required(login_url = 'login')
def my_orders(request):
    # ===> we are putting the [' - '] hypen ['-created_at'] because by using the hypen it will filter or get iyt in the descending order.
    orders  = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)



# =====> edit_profile views <=====
@login_required(login_url = 'login')
def edit_profile(request):
    # we are using [get_object_or_404] it is because it will get the user profile , and if there is no userprofile then it will return a 404 error
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        # we are using [instance] because we are updating the user profile.
        user_form = UserForm(request.POST, instance=request.user)
        # we are passing the [FILES] because we are using the FILES TYPE IN our form to upload files you must use request.FILES
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        # checking if both [user_form] and [profile_form] are valid, if there they are both valid then we are going to save the data
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated')
            return redirect('edit_profile')
    else:
        # you will see the existing data inside the form
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form' : user_form,
        'profile_form' : profile_form,
        'userprofile' : userprofile
    }
    return render(request,'accounts/edit_profile.html', context)



  
# =====> Change Password views <=====
@login_required(login_url = 'login')
def change_password(request):
    if request.method == 'POST':
        current_password  = request.POST['current_password']
        new_password  = request.POST['new_password']
        confirm_password  = request.POST['confirm_password']
        
         
        
        # the username from the Account from the create user method
        # the [__exact] will check if the username match with the one in the database it will only be case sensitive.
        user = Account.objects.get(username__exact = request.user.username)

        if new_password == confirm_password:
            # we are checking the password , if you dont use the [check_password] the we might not even know the password, the user is typing as current password.
            # if the current_password is wrong the system with not allow him to reset the password.
            # we can not just check it because it is already hashed [.check_password]
            success = user.check_password(current_password)
            # if the password is giving is the correct one
            if success:
                # it will set the password. and store it in a hashed format. so that nobody can read
                user.set_password(new_password)
                user.save()
                # even though you dont you put auth.logout(request) django will automatically log you out
                # auth.logout(request)
                # You can also log out when you set your password.
                # =====> when you use [ auth.logout(request) ] it will log you out as soon as you have created set your passsword.so you will have to log in again
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')

            # if the current password is not correct
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
            # if the new password and confirm password are not the same.
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')



# =====> Order detail views <=====
@login_required(login_url = 'login')
def order_detail(request, order_id):
    # [__order_number] this means that from the OrderProduct model, which means the [order] from the model and the [order_number] from another model because we are using a foreignKey, the [__] underscore we can use it to access the foreignKey fields 
    order_detail = OrderProduct.objects.filter(order__order_number = order_id)
    # getting the order by their id
    order = Order.objects.get(order_number = order_id)
    subtotal = 0

    for i in order_detail:
        subtotal += i.product_price * i.quantity
    
    context = {
        'order_detail' : order_detail,
        'order' : order,
        'subtotal' : subtotal
    }
    return render(request, 'accounts/order_detail.html', context)