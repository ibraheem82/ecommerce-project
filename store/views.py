# from django.http import HttpResponse
from itertools import product
from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product, ReviewRating,ProductGallery
from category.models import Category
from carts.models import CartItem
from django.db.models import Q
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct
# Create your views here.
# ===> so that we can display the categories 
# ===> 
# @login_required
def store(request, category_slug=None):
    categories  = None
    products    = None

    # ===> if it is not found bring a 404 error
    # ===> if the slug is not none
    if category_slug != None:
        categories      = get_object_or_404(Category, slug=category_slug)
        products        = Product.objects.filter(category=categories, is_available=True)
        # ===> this paginator will work for each categories products
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        # ===> we are getting the pages products
        paged_products = paginator.get_page(page)
        # ===> count all the available products
        product_count   = products.count()
    else:
        # ===> we are showing only the products that are available
        products = Product.objects.all().filter(is_available=True).order_by('id')
        
         # <===> These codes here works for the paginator  <===>
        # ===> we are passing the products and the numbers of products we wants to show
        # ===> we are capturing the url that comes with the page number, which means from the GET request
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        # ===> we are getting the pages products
        paged_products = paginator.get_page(page)
       
        
        # ===> we are counting the result of the products
        product_count = products.count()
    
        
    context = {
        'products' : paged_products,
        # 'products' : products,
        'product_count': product_count
    }
    
    
    
    return render(request, 'store/store.html', context)


# @login_required
def product_detail(request, category_slug, product_slug):
    try:
        # ===> we should be able to see the products detail
        single_product = Product.objects.get(category__slug = category_slug, slug = product_slug)
        
        # ===> check if the product exist in the cartitem
        # ===> 'cart__' this means that we are checking the Cart' model, because the 'Cart' is ForeignKey of the Cartitem
        # ===> and accessing the cart_id
        # ===> '_cart_id(request)' this is the private function we created that stores the session key,
        # ===> we have to import it
        # ===> if this <===> in_cart = CartItem.objects.filter(cart__cart_id =_cart_id(request), product = single_product).exists() <===> returns anything or has any object, it is going to return true, true means that we are not going to show the add to cart button., if false then the product is not in the cart
        in_cart = CartItem.objects.filter(cart__cart_id =_cart_id(request), product = single_product).exists()
        
    except Exception as e:
        raise e
    if request.user.is_authenticated:
        try:
            # ===> Make sure only the user that purchase the product can make a review 
            # ===> we are getting ['single_product.id'] a single_product by it id
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None
        
        
        
    # ===> Get the reviews
    # ===> ['status = True'] by default the status is true but the admin can set it to false if he wish to do so, so that, that particular review will not show in the website
    reviews = ReviewRating.objects.filter(product_id = single_product.id, status = True)
    
    
    # we want to get the product gallery
    # get the single product 
    product_gallery = ProductGallery.objects.filter(product_id = single_product.id)
    
    context = {
        'single_product': single_product,
        'in_cart'       : in_cart,
        'orderproduct'  : orderproduct,
        'reviews'       : reviews,
      'product_gallery' : product_gallery
    }
    
    return render(request, 'store/product_detail.html', context )



def search(request):
    # ===> we need to recieve what is coming from the url which is the get request
    # ===> we are checking if the get request has the keyword or not
    # ===> we are storing the value of that 'keyword' inside the keyword = variable
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        # ===> we are also checking if the keyword we are getting from the url is blank or not
        if keyword:
            # ===> '__icontains' means this will look for the whole description and if it found anything related to this '__icontains = keyword' keyword, it will bring that product and show it inside the particular place you are searching it.
            # ===> the 'Q' is the queryset
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains = keyword) | Q(product_name__icontains = keyword))       
            product_count = products.count()
        else:
            return render(request, 'store/store.html')
    
    context = {
        'products' : products,
        'product_count' : product_count,
    }
    
    
    return render(request, 'store/store.html', context)



def submit_review(request, product_id):
    # ['request.META.get('HTTP_REFERER'] means that the url will be stored inside the url variable
    # ===> telling it to store the previous url
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            # ===> if there is a review by the user we are going to update it not delete it
            # ===> check if the review is already exist or not
            # ===> we are using ['user__id'] beacuse if you check the review rating we are refering to the users id i.e the account user id with a foreingkey 
            # ===> this ['product_id'] is the product id in the ['submit_review'] function
            # ===> the ['product__id'] is the product in the ['ReviewRating'] model and it id it id is the product model
            # ===> double underscore to access the id of that product ['__id']
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id) 
            # ===> in the ['(request.POST'] we will be having all the data from the review form
            # ===> we are passing this ['instance=reviews'] because we want to check if there is already a review, so hv to update that review
            # ===> if you dont pass this ['instance=reviews'] it will create a new review if there is already a review by this user for the product, then we need to update that review, not create a new one 
            # ===> by using this ['instance=reviews'] our form will understand that we want to update the records
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            # ===> this is not updated not created because we are passing ['instance=reviews'].
            messages.success(request, 'Thank you! Your review has been updated.')
            # ===> we want to redirect the user the current page they are on.
            return redirect(url)
            
            
            
        except ReviewRating.DoesNotExist:
            # ===> if there is not review by the user and the user create a new review we are going to create it.
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                # ===> this ['equest.META.get('REMOTE_ADDR'] will store the ip address
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user.id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)