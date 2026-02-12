from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import authenticate
from .models import User, Property, Transaction
from .serializers import UserSerializer, PropertySerializer, TransactionSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'register', 'me']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data['password'])
            user.save()
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
        property.status = 'approved'
        property.save()
        return Response({'status': 'Property approved'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def purchase(self, request, pk=None):
        property = self.get_object()
        if property.status != 'approved':
            return Response({'error': 'Property not available for purchase'}, status=status.HTTP_400_BAD_REQUEST)
        if property.seller == request.user:
            return Response({'error': 'Cannot purchase your own property'}, status=status.HTTP_400_BAD_REQUEST)

        # Create transaction
        transaction = Transaction.objects.create(
            property=property,
            buyer=request.user,
            amount=property.price
        )
        property.status = 'sold'
        property.save()

        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(buyer=self.request.user) | Transaction.objects.filter(property__seller=self.request.user)
