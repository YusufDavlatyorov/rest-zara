from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import ProductVariant
from drf_yasg.utils import swagger_auto_schema


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def get(self, request):
        """Получить корзину"""
        cart = self.get_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CartItemSerializer)
    def post(self, request):
        """Добавить товар в корзину"""
        serializer = CartItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        variant_id = serializer.validated_data['variant_id']
        quantity = serializer.validated_data.get('quantity', 1)

        variant = ProductVariant.objects.get(id=variant_id)
        cart = self.get_cart(request.user)
        
        item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)

        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity

        if item.quantity > variant.stock:
            return Response({'detail': f'Not enough stock. Max available: {variant.stock}'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        item.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    def delete(self, request):
        """Очистить всю корзину"""
        cart = self.get_cart(request.user)
        cart.items.all().delete()
        return Response({'detail': 'Cart cleared.'}, status=status.HTTP_200_OK)


class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=CartItemSerializer) # Добавил схему для PATCH
    def patch(self, request, item_id):
        """Изменить количество товара в корзине"""
        quantity = request.data.get('quantity')
        
        if quantity is None or int(quantity) < 1:
            return Response({'detail': 'Invalid quantity.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)

        if int(quantity) > item.variant.stock:
            return Response({'detail': f'Not enough stock. Only {item.variant.stock} left.'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        item.quantity = int(quantity)
        item.save()

        return Response(CartSerializer(item.cart).data)

    def delete(self, request, item_id):
        """Удалить один товар из корзины"""
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)

        cart = item.cart
        item.delete()
        return Response(CartSerializer(cart).data)
