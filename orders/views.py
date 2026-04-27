from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer, CreateOrderSerializer, AdminOrderSerializer
from accounts.permissions import IsAdminRole


class OrderListView(generics.ListAPIView):
    """Список заказов текущего юзера"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class OrderDetailView(generics.RetrieveAPIView):
    """Детали одного заказа — только своего"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class CreateOrderView(APIView):
    """Создать заказ из корзины"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CancelOrderView(APIView):
    """Отменить заказ — только если pending"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(id=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        if order.status != Order.Status.PENDING:
            return Response(
                {'detail': 'Only pending orders can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Возвращаем stock
        for item in order.items.select_related('variant'):
            if item.variant:
                item.variant.stock += item.quantity
                item.variant.save()

        order.status = Order.Status.CANCELLED
        order.save()
        return Response(OrderSerializer(order).data)


# --- Admin ---

class AdminOrderListView(generics.ListAPIView):
    """Все заказы — только для admin"""
    serializer_class = AdminOrderSerializer
    permission_classes = [IsAdminRole]
    queryset = Order.objects.all().prefetch_related('items').select_related('user')


class AdminOrderUpdateView(generics.RetrieveUpdateAPIView):
    """Изменить статус заказа — только для admin"""
    serializer_class = AdminOrderSerializer
    permission_classes = [IsAdminRole]
    queryset = Order.objects.all()