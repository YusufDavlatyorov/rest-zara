from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from .models import Category, Product
from .serializers import CategorySerializer, ProductListSerializer, ProductDetailSerializer
from .filters import ProductFilter
from accounts.permissions import IsAdminRole

# --- КАТЕГОРИИ ---
class CategoryListView(generics.ListAPIView):
    # Показываем только главные категории, вложенные подтянутся через Serializer
    queryset = Category.objects.filter(parent=None).prefetch_related('children')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

# --- ТОВАРЫ (Публичные) ---
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True).prefetch_related(
        'images', 'variants__color', 'variants__size'
    )
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True).prefetch_related(
        'images__color', 'variants__color', 'variants__size', 'category'
    )
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

# --- АДМИН-ПАНЕЛЬ ---
class ProductCreateView(generics.CreateAPIView):
    # Использует твой исправленный метод .create() из сериализатора
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAdminRole]

class ProductUpdateView(generics.RetrieveUpdateDestroyAPIView):
    # Добавляем prefetch для корректного отображения при обновлении
    queryset = Product.objects.all().prefetch_related('images', 'variants')
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAdminRole]
    lookup_field = 'slug'
