from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductVariantSerializer, ProductImageSerializer
from products.models import ProductImage


class CartItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.IntegerField(write_only=True)
    total_price = serializers.ReadOnlyField()
    product_name = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'variant', 'variant_id',
            'quantity', 'total_price',
            'product_name', 'main_image'
        ]

    def get_product_name(self, obj):
        return obj.variant.product.name

    def get_main_image(self, obj):
        image = ProductImage.objects.filter(
            product=obj.variant.product,
            color=obj.variant.color,
            is_main=True
        ).first()
        if image:
            return ProductImageSerializer(image).data
        return None

    def validate_variant_id(self, value):
        from products.models import ProductVariant
        try:
            variant = ProductVariant.objects.get(id=value)
        except ProductVariant.DoesNotExist:
            raise serializers.ValidationError("Variant not found.")
        if variant.stock <= 0:
            raise serializers.ValidationError("This variant is out of stock.")
        return value


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'total_items', 'updated_at']