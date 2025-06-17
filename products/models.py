from django.db import models
from .models import *
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission, BaseUserManager
from decimal import Decimal



class UserType(models.Model):
   
    usertype = models.CharField(max_length=100)
 
    def __str__(self):
        return self.usertype
    

class Category(models.Model):
   
    category_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    def __str__(self):
        return self.category_name   




class Product(models.Model):
    SKU = models.CharField(max_length=100, unique=True)
    product_name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')    
    gross_weight = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    diamond_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    colour_stones = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    net_weight = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    product_image = models.ImageField(upload_to='products/', blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    usertypes = models.ManyToManyField(UserType, related_name='products_usertype')

    def __str__(self):
        return self.product_name
     
   
    def format_weight(self, weight):
        if weight is not None:
            return '{:g}'.format(weight)
        return None
    
    

class ProductMultipleImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='products/additional_images')

    def __str__(self):
        return f"Additional Image for {self.product.product_name}"
    
    
    
class CustomizedProduct(models.Model):
    SKU = models.CharField(max_length=100, unique=True)
    product_name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='customized_products')
    gross_weight = models.DecimalField(max_digits=10, decimal_places=3,blank=True, null=True)
    diamond_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    colour_stones = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    net_weight = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)   
    product_image = models.ImageField(upload_to='cus_products/', blank=True, null=True)
    description = models.TextField(null=True,blank=True)
    usertypes = models.ManyToManyField(UserType, related_name='cus_products_usertype')

    def __str__(self):
        
        return self.product_name
    
    def format_weight(self, weight):
        if weight is not None:
            return '{:g}'.format(weight)
        return None
    
class CustomizedProductMultipleImages(models.Model):
    product = models.ForeignKey(CustomizedProduct, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='cus_products/additional_images')

    def __str__(self):
        return f"Additional Image for {self.product.product_name}"
    


 

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, blank=True)
    mobile_number = models.CharField(max_length=15, blank=True)
    whatsapp_number = models.CharField(max_length=15, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    shipping_address = models.TextField(blank=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    company_email = models.EmailField(blank=True)
    company_website = models.CharField(max_length=128, blank=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    usertypes = models.ForeignKey(UserType, on_delete=models.CASCADE, related_name='users',null=True)
    prof_image =  models.ImageField(upload_to='user_proifle/', blank=True, null=True)
    
  
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    
    groups = models.ManyToManyField(
        Group,
        related_name="products_user_set",  
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="products_user_permissions", 
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email




class Media(models.Model):
    image = models.ImageField(upload_to='media')

    def __str__(self):
        return f"Image {self.id}"

     
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='carts')
    quantity = models.PositiveIntegerField(default=1)
    gross_weight = models.DecimalField(max_digits=10, decimal_places=3,  blank=True, null=True)
    color = models.CharField(max_length=100,null = True)
    diamond_weight = models.DecimalField(max_digits=10, decimal_places=2,  blank=True, null=True)
    colour_stones = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    net_weight = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.product.product_name} (Quantity: {self.quantity})"
    def format_weight(self, weight):
        if weight is not None:
            return '{:g}'.format(weight)
        return None

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('delivered', 'delivered'),
        ('accepted', 'accepted'),
         
    ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    ordercode = models.CharField(max_length=255, blank=True)
    total_gross_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_diamond_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_colour_stones = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_net_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"Order {self.user_id} by {self.user.email}"
     
        
        
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=100,null = True)
    additional_notes = models.TextField(blank=True, null=True)   

    def __str__(self):
        return f"{self.product.product_name} (Quantity: {self.quantity}) in Order {self.order_id}"


class Color(models.Model):
    color = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.color
    

class CustomizedOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]   
    NEW_STATUS_CHOICES = [
        ('processed','Processed'),
        ('cad', 'CAD'),
        ('cam', 'CAM'),
        ('wax','WAX'),
        ('casting','Casting'),
        ('grilling','Grilling'),
        ('filling','filling'),
        ('pre polish','Pre Polish'),
        ('setting','Setting'),
        ('final polish','Final Polish'),
        ('rhoium','Rhoium'),
        ('final qc','Final QC'),
        ('certification','Certification'),
        ('invoice','Invoice'),
        ('out for delivery','Out For Delivery'),
        ('delivered','Delivered')
        
    ]  
    product = models.ForeignKey(CustomizedProduct, on_delete=models.CASCADE, related_name='orders')
    ordercode = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customized_orders')
    size = models.CharField(max_length=100)
    gram = models.DecimalField(max_digits=10, decimal_places=2)
    cent = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, default=True, related_name='colors')
    description = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')   
    new_status = models.CharField(max_length=20, choices=NEW_STATUS_CHOICES, default='processed') 
    due_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} for {self.product.product_name} by {self.user.username}"
 

class FullCustomizedOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    NEW_STATUS_CHOICES = [
        ('processed','Processed'),
        ('cad', 'CAD'),
        ('cam', 'CAM'),
        ('wax','WAX'),
        ('casting','Casting'),
        ('grilling','Grilling'),
        ('filling','filling'),
        ('pre polish','Pre Polish'),
        ('setting','Setting'),
        ('final polish','Final Polish'),
        ('rhoium','Rhoium'),
        ('final qc','Final QC'),
        ('certification','Certification'),
        ('invoice','Invoice'),
        ('out for delivery','Out For Delivery'),
        ('delivered','Delivered')
        
    ] 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='full_customized_orders')    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='full_customized_products')
    design_number = models.CharField(max_length=100, default=True)
    size = models.CharField(max_length=100)
    gram = models.DecimalField(max_digits=10, decimal_places=2)
    cent = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='full_colors')   
    description = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    ordercode = models.CharField(max_length=100, null=True, blank=True)   
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending') 
    new_status = models.CharField(max_length=20, choices=NEW_STATUS_CHOICES, default='processed') 
    due_date = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class FullCustomizedMultipleImages(models.Model):
    product_images = models.ForeignKey(FullCustomizedOrder, on_delete=models.CASCADE, related_name='full_additional_images')
    image = models.ImageField(upload_to='cus_products/additional_images')

    def __str__(self):
        return f"Additional Image for order {self.product_images.id}" 

class ContactMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default = True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.full_name} at {self.created_at}"
