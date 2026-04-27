import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category__slug')
    color = django_filters.CharFilter(field_name='variants__color__name', lookup_expr='iexact')
    size = django_filters.CharFilter(field_name='variants__size__name', lookup_expr='iexact')

    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'category', 'color', 'size']