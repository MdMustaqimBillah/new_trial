from rest_framework import viewsets
from .models import Product
from rest_framework.permissions import IsAuthenticated
from .serializers import ProductSerializer
from permissions.custom_permissions import IsAdminOrReadOnly

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated,IsAdminOrReadOnly]
