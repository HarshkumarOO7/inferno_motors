from django.db import models
from django.utils.html import format_html
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator
class UserDetailsManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, name, password, **extra_fields)


class userdetails(AbstractBaseUser):
    name = models.CharField(max_length=75)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=25, blank=True, null=True)
    contact = models.CharField(max_length=12, blank=True, null=True)

    # Add these fields for Django's authentication system
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Define REQUIRED_FIELDS
    REQUIRED_FIELDS = ['name']

    # Define USERNAME_FIELD
    USERNAME_FIELD = 'email'

    # Use the custom manager
    objects = UserDetailsManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


# Car Company Model
class CarCompany(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='car_companies/', null=True, blank=True)

    def __str__(self):
        return self.name

    def image_tag(self):
        if self.image:
            return format_html('<img src="{}" width="100" height="100" style="border-radius:5px;"/>', self.image.url)
        return "-"
    image_tag.short_description = 'Company Logo'

# Car Model
class CarModel(models.Model):
    company = models.ForeignKey(CarCompany, on_delete=models.CASCADE, related_name='car_models')
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='car_models/', null=True, blank=True)

    def __str__(self):
        return f"{self.company.name} - {self.name}"

    def image_tag(self):
        if self.image:
            return format_html('<img src="{}" width="100" height="100" style="border-radius:5px;"/>', self.image.url)
        return "-"
    image_tag.short_description = 'Model Image'

# Car Part Model
class CarPart(models.Model):
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name='car_parts')
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='car_parts/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.car_model.company.name} - {self.car_model.name} - {self.name}"

    def is_available(self):
        return self.quantity > 0

    def image_tag(self):
        if self.image:
            return format_html('<img src="{}" width="100" height="100" style="border-radius:5px;"/>', self.image.url)
        return "-"
    image_tag.short_description = 'Part Image'


class CarPartsPurchase(models.Model):
    user = models.ForeignKey(userdetails, on_delete=models.CASCADE)  # Changed from User to userdetails
    part = models.ForeignKey('CarPart', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    purchase_date = models.DateField(default=timezone.now)
    address = models.TextField()
    payment_status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.part.name} - {self.quantity}"  # Changed from username to email

    def total_price(self):
        return self.part.price * self.quantity


class Car(models.Model):
    FUEL_TYPES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('cng', 'CNG'),
    ]

    TRANSMISSION_TYPES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
    ]

    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    mileage = models.PositiveIntegerField(help_text="In kilometers")
    fuel_type = models.CharField(max_length=10, choices=FUEL_TYPES)
    transmission = models.CharField(max_length=10, choices=TRANSMISSION_TYPES)
    color = models.CharField(max_length=30)
    engine_capacity = models.PositiveIntegerField(help_text="In cc")
    description = models.TextField()
    location = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_sold = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"


class CarImage(models.Model):
    car = models.ForeignKey(Car, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='car_images/')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.car}"


class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchase request for {self.car} by {self.buyer}"


class Car(models.Model):
    FUEL_TYPES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('cng', 'CNG'),
    ]

    TRANSMISSION_TYPES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
    ]

    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    mileage = models.PositiveIntegerField(help_text="In kilometers")
    fuel_type = models.CharField(max_length=10, choices=FUEL_TYPES)
    transmission = models.CharField(max_length=10, choices=TRANSMISSION_TYPES)
    color = models.CharField(max_length=30)
    engine_capacity = models.PositiveIntegerField(help_text="In cc")
    description = models.TextField()
    location = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_sold = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"


class CarImage(models.Model):
    car = models.ForeignKey(Car, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='car_images/')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.car}"


class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('countered', 'Counter Offer'),
    ]

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='purchase_requests')
    buyer_name = models.CharField(max_length=100)
    buyer_email = models.EmailField()
    buyer_phone = models.CharField(max_length=15)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request for {self.car} by {self.buyer_name}"