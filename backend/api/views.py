from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
<<<<<<< HEAD
=======
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import authenticate
from django.utils import timezone
>>>>>>> d46dae8ee07e36925c9de3218838663f7c31ace1
from .models import User, Property, Transaction
from .serializers import UserSerializer, PropertySerializer, TransactionSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'register']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Property.objects.all()
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def create(self, request, *args, **kwargs):
        if request.user.role not in ['seller', 'admin']:
            return Response({'error': 'Only sellers and admins can create properties'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        if request.user.role != 'admin':
            return Response({'error': 'Only admins can approve properties'}, status=status.HTTP_403_FORBIDDEN)
        property = self.get_object()
        # Prevent approval of already sold properties
        if property.status == 'sold':
            return Response({'error': 'Cannot approve a property that has already been sold'}, status=status.HTTP_400_BAD_REQUEST)
        property.status = 'approved'
        property.save()
        return Response({'status': 'Property approved'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def purchase(self, request, pk=None):
        """Initiate a purchase - creates a pending transaction"""
        property = self.get_object()
        if property.status != 'approved':
            return Response({'error': 'Property not available for purchase'}, status=status.HTTP_400_BAD_REQUEST)
        if property.seller == request.user:
            return Response({'error': 'Cannot purchase your own property'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if there's already a pending transaction for this property
        existing_transaction = Transaction.objects.filter(property=property, payment_status='pending').first()
        if existing_transaction:
            serializer = TransactionSerializer(existing_transaction)
            return Response(serializer.data)

        # Create transaction with pending payment status (do NOT mark property as sold yet)
        transaction = Transaction.objects.create(
            property=property,
            buyer=request.user,
            amount=property.price,
            payment_status='pending'
        )

        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def process_payment(self, request, pk=None):
        """Process payment for a transaction - marks property as sold after payment"""
        property = self.get_object()
        
        # Find the pending transaction for this property
        transaction = Transaction.objects.filter(property=property, buyer=request.user, payment_status='pending').first()
        
        if not transaction:
            return Response({'error': 'No pending transaction found for this property'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get payment method from request
        payment_method = request.data.get('payment_method')
        if not payment_method:
            return Response({'error': 'Payment method is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update transaction with payment details
        transaction.payment_method = payment_method
        transaction.payment_status = 'completed'
        transaction.payment_date = timezone.now()
        transaction.save()
        
        # Mark property as sold
        property.status = 'sold'
        property.save()
        
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(buyer=self.request.user) | Transaction.objects.filter(property__seller=self.request.user)
