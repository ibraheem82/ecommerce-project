from audioop import reverse
from django.db import models
from django.urls import reverse

# Create your models here.


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    # ===> Url of the category
    slug = models.SlugField(max_length = 100,unique=True)
    description = models.TextField(max_length = 255, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)
    
    
    # ===> overiding the name category in the django admin panel 
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        
        
    # ===> this will bring us the url of a particular category
    # ===> 'get_url' will be use in the loop in the header templates
    def get_url(self):
        # ===> 'products_by_category' is the name of the category slug used in the url
        return reverse('products_by_category', args=[self.slug])    
    
    
    
    def __str__(self):
        return self.category_name