from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductImageSerializer
from products.models import ProductImage


class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.ReadOnlyField()
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_name', 'color_name',
            'size_name', 'price', 'quantity',
            'total_price', 'main_image'
        ]

    def get_main_image(self, obj):
        if obj.variant:
            image = ProductImage.objects.filter(
                product=obj.variant.product,
                color=obj.variant.color,
                is_main=True
            ).first()
            if image:
                return ProductImageSerializer(image).data
        return None


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'shipping_address', 'phone',
            'total_price', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['status', 'total_price', 'created_at', 'updated_at']


class CreateOrderSerializer(serializers.Serializer):
    shipping_address = serializers.CharField()
    phone = serializers.CharField(max_length=20)

    def validate(self, attrs):
        user = self.context['request'].user
        cart = user.cart
        if not cart.items.exists():
            raise serializers.ValidationError("Cart is empty.")
        return attrs

    def create(self, validated_data):
        from cart.models import CartItem
        user = self.context['request'].user
        cart = user.cart

        for item in cart.items.select_related('variant'):
            if item.quantity > item.variant.stock:
                raise serializers.ValidationError(
                    f"'{item.variant.product.name}' - not enough stock."
                )


        order = Order.objects.create(
            user=user,
            shipping_address=validated_data['shipping_address'],
            phone=validated_data['phone'],
            total_price=cart.total_price
        )

        for item in cart.items.select_related('variant__product', 'variant__color', 'variant__size'):
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                product_name=item.variant.product.name,
                color_name=item.variant.color.name,
                size_name=item.variant.size.name,
                price=item.variant.product.final_price,
                quantity=item.quantity
            )
            # Уменьшаем stock
            item.variant.stock -= item.quantity
            item.variant.save()

        # Очищаем корзину
        cart.items.all().delete()

        return order


class AdminOrderSerializer(serializers.ModelSerializer):
    """Для admin — можно менять статус"""
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'status', 'shipping_address', 'phone',
            'total_price', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'total_price', 'created_at']