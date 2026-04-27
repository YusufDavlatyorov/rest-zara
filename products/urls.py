from django.urls import path
from .views import (
    CategoryListView, ProductListView,
    ProductDetailView, ProductCreateView, ProductUpdateView
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryListView.as_view(), ),
    path('', ProductListView.as_view(), name='product-list'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),


    path('admin/create/', ProductCreateView.as_view(), name='product-create'),
    path('admin/<slug:slug>/edit/', ProductUpdateView.as_view(), name='product-update'),
]