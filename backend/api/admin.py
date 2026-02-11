from django.contrib import admin
from .models import User, Property, Transaction
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role')
    search_fields = ('username', 'email')

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'address', 'price', 'seller', 'status', 'created_at')
    search_fields = ('title', 'address', 'seller__username')
    list_filter = ('status', 'created_at')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'property', 'amount', 'transaction_date')
    search_fields = ('buyer__username', 'property__title')
    list_filter = ('transaction_date',)
    
