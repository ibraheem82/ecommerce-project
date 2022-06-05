# we have to let the settings.py known that we are using context_processors
from .models import Category

# ===> it takes a request as an argument and it will return the dictionary of the data as a context
# ===> 
def menu_links(request):
    # ===> fetching all the categories from the database 
    # ===> it will store all the categories into the links variable
    links = Category.objects.all()
    # ===> we acn use the links whereever we want
    return dict(links = links)
# ===> Go to settings.py for proper configurations