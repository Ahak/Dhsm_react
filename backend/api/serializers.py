from rest_framework import serializers
from .models import User, Property, Transaction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'image']
        read_only_fields = ['id']

class PropertySerializer(serializers.ModelSerializer):
    seller = UserSerializer(read_only=True)

    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class TransactionSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    buyer = UserSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'property', 'buyer', 'amount', 'transaction_date', 'payment_status', 'payment_method', 'payment_date']
        read_only_fields = ['id', 'transaction_date']
