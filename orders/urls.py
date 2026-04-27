from django.urls import path
from .views import (
    OrderListView, OrderDetailView,
    CreateOrderView, CancelOrderView,
    AdminOrderListView, AdminOrderUpdateView
)

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('create/', CreateOrderView.as_view(), name='order-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/cancel/', CancelOrderView.as_view(), name='order-cancel'),
    path('admin/', AdminOrderListView.as_view(), name='admin-order-list'),
    path('admin/<int:pk>/', AdminOrderUpdateView.as_view(), name='admin-order-update'),
]