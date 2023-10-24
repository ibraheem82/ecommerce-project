from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

 # ===> Creating a model for super admin
#  ===>  Creating a custom user model
class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        # ===> raise error if not email address
        if not email:
            raise ValueError('User must have an email address')
        
        if not username:
            raise ValueError('User must have a username')
        
        user = self.model(
             # what the 'normalize_email' does is that if you enter a capital letter inside your email it will change it so small letter everything will be normalized
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )
        
         # ===> the 'set_password' is use for setting the password
        user.set_password(password)
        user.save(using=self._db)
        # Create a UserProfile for the superuser
        UserProfile.objects.create(user=user)
        return user
    
     # ===> creating the superUser
     # ------- Creating the SuperUser --------
    def create_superuser(self, first_name, last_name, username, email, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
        )
     # ===> giving the permisson
     # ===> set it to true
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        # * Create a UserProfile for the user
        UserProfile.objects.create(user=user)
        return user
    





# # Create your models here.
# # ===> this custom user model will be use to overide the django admin panel system
class Account(AbstractBaseUser):
    first_name          = models.CharField(max_length=50)
    last_name           = models.CharField(max_length=50)
    username            = models.CharField(max_length=50, unique=True)
    email               = models.EmailField(max_length = 100, unique=True)
    phone_number        = models.CharField(max_length=50)
    
#     # ===> these fields are madantory when creating custom user model
#     # ===> Required
    date_joined         = models.DateTimeField(auto_now_add=True)
    last_login          = models.DateTimeField(auto_now_add=True)
    is_admin            = models.BooleanField(default=False)
    is_staff            = models.BooleanField(default=False)
    is_active           = models.BooleanField(default=False)
    is_superadmin       = models.BooleanField(default=False)


#     # ===>
#     # ===> Overiding the login field
#     # ===> By default username is login field to the admin panel 
#     # ===> but in this application we want to login with our email address to the django admin panel
#     # ===> we set the usernameField to email so that we can loggin with our email address
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    objects = MyAccountManager()
    
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
#     # when we return an account object in the template we should return an email
    def __str__(self):
        return self.email
    
    
#     # ===> Mandatory Methods
#     # ===> perm is the permisson
    def has_perm(self, perm, obj=None):
#         # ===> if the user is the admin he has the permission to do all the changes
        return self.is_admin
    
    def has_module_perms(slef, add_label):
        return True

class UserProfile(models.Model):
    # ===> we are use [ OnetoOneField() ] because the it is also like a foreignkey but the difference is the [ OnetoOneField() ] is unique OnetoOneField() means you can have only one profile for just one account, but if you use a foreignkey you can have multiple profile for one user
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    address_line_1 = models.CharField(blank = True, max_length = 100)
    address_line_2 = models.CharField(blank = True, max_length = 100)
    profile_picture = models.ImageField(blank=True, upload_to = 'userprofile')
    city = models.CharField(blank=True, max_length=20)
    state = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=20)
    
    def get_profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        else:
            # Set a default profile picture URL here.
            return '/media/image/default_profile_picture.png'



    def __str__(self):
        return self.user.first_name



    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'