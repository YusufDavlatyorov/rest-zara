from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_name', 'color_name', 
            'size_name', 'price', 'quantity', 'total_price'
        ]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'shipping_address', 'phone', 
            'total_price', 'items', 'created_at'
        ]
        read_only_fields = ['status', 'total_price']

class CreateOrderSerializer(serializers.ModelSerializer):
    # Добавляем поле для ввода ID корзины
    cart_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ['shipping_address', 'phone', 'cart_id']

    def validate(self, attrs):
        user = self.context['request'].user
        cart_id = attrs.get('cart_id')
        
        # Импортируем внутри, чтобы избежать циклической зависимости
        from cart.models import Cart
        
        try:
            # Ищем корзину по ID и проверяем, принадлежит ли она юзеру
            cart = Cart.objects.get(id=cart_id, user=user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError({"detail": "Корзина с таким ID не найдена."})

        if not cart.items.exists():
            raise serializers.ValidationError({"detail": "Корзина пуста."})
        
        # Сохраняем объект корзины в атрибуты для метода create
        attrs['cart_obj'] = cart
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        cart = validated_data.pop('cart_obj') # Берем найденную корзину

        order = Order.objects.create(
            user=user,
            shipping_address=validated_data['shipping_address'],
            phone=validated_data['phone'],
            total_price=cart.total_price
        )

        for item in cart.items.select_related('variant__product'):
            if item.quantity > item.variant.stock:
                raise serializers.ValidationError(
                    {"detail": f"'{item.variant.product.name}' - недостаточно на складе."}
                )
            
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                product_name=item.variant.product.name,
                color_name=item.variant.color.name,
                size_name=item.variant.size.name,
                price=item.variant.product.final_price,
                quantity=item.quantity
            )
            item.variant.stock -= item.quantity
            item.variant.save()

        cart.items.all().delete()
        return order


    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        cart = user.cart

        order = Order.objects.create(
            user=user,
            shipping_address=validated_data['shipping_address'],
            phone=validated_data['phone'],
            total_price=cart.total_price
        )

        for item in cart.items.select_related('variant__product', 'variant__color', 'variant__size'):
            if item.quantity > item.variant.stock:
                raise serializers.ValidationError(
                    {"detail": f"Not enough stock for {item.variant.product.name}"}
                )
            
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                product_name=item.variant.product.name,
                color_name=item.variant.color.name,
                size_name=item.variant.size.name,
                price=item.variant.product.final_price,
                quantity=item.quantity
            )
            
            item.variant.stock -= item.quantity
            item.variant.save()

        cart.items.all().delete()
        return order

class AdminOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_email', 'status', 'shipping_address', 
            'phone', 'total_price', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'total_price', 'created_at', 'updated_at']
