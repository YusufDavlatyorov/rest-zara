from rest_framework import serializers
from .models import Category, Product, Color, Size, ProductVariant, ProductImage

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'children']

    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'hex_code']

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main', 'order', 'color']

class ProductVariantSerializer(serializers.ModelSerializer):
    color = ColorSerializer()
    size = SizeSerializer()

    class Meta:
        model = ProductVariant
        fields = ['id', 'color', 'size', 'stock', 'sku']

class ProductListSerializer(serializers.ModelSerializer):
    colors = serializers.SerializerMethodField(read_only=True)
    main_image = serializers.SerializerMethodField(read_only=True)
    final_price = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'discount_price', 'final_price', 'main_image', 'colors']

    def get_colors(self, obj):
        color_ids = obj.variants.values_list('color', flat=True).distinct()
        colors = Color.objects.filter(id__in=color_ids)
        return ColorSerializer(colors, many=True).data

    def get_main_image(self, obj):
        image = obj.images.filter(is_main=True).first()
        return ProductImageSerializer(image).data if image else None

# --- ИСПРАВЛЕННЫЙ ДЕТАЛЬНЫЙ СЕРИАЛИЗАТОР ---
class ProductDetailSerializer(serializers.ModelSerializer):
    images_by_color = serializers.SerializerMethodField(read_only=True)
    variants = ProductVariantSerializer(many=True)
    colors = serializers.SerializerMethodField(read_only=True)
    sizes = serializers.SerializerMethodField(read_only=True)
    final_price = serializers.ReadOnlyField()
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price',
            'discount_price', 'final_price', 'category',
            'colors', 'sizes', 'variants', 'images_by_color'
        ]

    def create(self, validated_data):
        category_data = validated_data.pop('category')
        variants_data = validated_data.pop('variants')


        category_slug = category_data.pop('slug')
        category, _ = Category.objects.get_or_create(slug=category_slug, defaults=category_data)
        product = Product.objects.create(category=category, **validated_data)

        for variant in variants_data:
            color_data = variant.pop('color')
            size_data = variant.pop('size')

            color, _ = Color.objects.get_or_create(
                name=color_data['name'], 
                defaults={'hex_code': color_data.get('hex_code', '#000000')}
            )
            size, _ = Size.objects.get_or_create(name=size_data['name'])

            ProductVariant.objects.create(
                product=product,
                color=color,
                size=size,
                **variant
            )

        return product

    def get_images_by_color(self, obj):
        result = {}
        for image in obj.images.select_related('color').all():
            color_id = str(image.color.id)
            if color_id not in result:
                result[color_id] = []
            result[color_id].append(ProductImageSerializer(image).data)
        return result

    def get_colors(self, obj):
        color_ids = obj.variants.values_list('color', flat=True).distinct()
        colors = Color.objects.filter(id__in=color_ids)
        return ColorSerializer(colors, many=True).data

    def get_sizes(self, obj):
        size_ids = obj.variants.values_list('size', flat=True).distinct()
        sizes = Size.objects.filter(id__in=size_ids)
        return SizeSerializer(sizes, many=True).data
