from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('seller', 'Seller'),
        ('buyer', 'Buyer'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    image = models.ImageField(upload_to='user_images/', blank=True, null=True)

    def __str__(self):
        return self.username

class Property(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('sold', 'Sold'),
    ]
    title = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    image1 = models.ImageField(upload_to='property_images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='property_images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='property_images/', blank=True, null=True)
    bedrooms = models.IntegerField(default=0)
    bathrooms = models.IntegerField(default=0)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Transaction(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('card', 'Credit/Debit Card'),
    ]
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='transactions')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.buyer.username} - {self.property.title}"

