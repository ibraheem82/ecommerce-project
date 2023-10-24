from django.shortcuts import render
from store.models import Product, ReviewRating

# Create your views here.


def home(request):
    # ===> we are showing only the products that are available
    # ===> we are showing the products that are only available 
    products = Product.objects.all().filter(is_available=True).order_by('created_date')
    
    
    
     # ===> Get the reviews
    # ===> ['status = True'] by default the status is true but the admin can set it to false if he wish to do so, so that, that particular review will not show in the website
    for product in products:
        # we want to show the rating stars in the home page
        reviews = ReviewRating.objects.filter(product_id = product.id, status = True)
    
    context  = {
        'products' : products,
        'reviews'  : reviews,
    }
    return render(request, 'boldbase/home.html', context )
