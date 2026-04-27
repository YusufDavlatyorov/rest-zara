from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Order
from .serializers import OrderSerializer, CreateOrderSerializer, AdminOrderSerializer
from accounts.permissions import IsAdminRole
from drf_spectacular.utils import extend_schema

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__variant__product')

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__variant__product')

class CreateOrderView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateOrderSerializer 

    @extend_schema(request=CreateOrderSerializer) 
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        try:
            order = Order.objects.select_for_update().get(id=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        if order.status != Order.Status.PENDING:
            return Response(
                {'detail': 'Only pending orders can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for item in order.items.select_related('variant'):
            if item.variant:
                item.variant.stock += item.quantity
                item.variant.save()

        order.status = Order.Status.CANCELLED
        order.save()
        return Response(OrderSerializer(order).data)

class AdminOrderListView(generics.ListAPIView):
    serializer_class = AdminOrderSerializer
    permission_classes = [IsAdminRole]
    queryset = Order.objects.all().select_related('user').prefetch_related('items__variant__product')

class AdminOrderUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = AdminOrderSerializer
    permission_classes = [IsAdminRole]
    queryset = Order.objects.all().select_related('user')
