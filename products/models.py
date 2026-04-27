from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='children'
    )
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price


class Color(models.Model):
    name = models.CharField(max_length=50)       # "Red", "Black"
    hex_code = models.CharField(max_length=7)    # "#FF0000"

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=10)       # "XS", "S", "M", "L", "XL"

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    """Каждый вариант = продукт + цвет + размер"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.product.name} - {self.color.name} - {self.size.name}"

    class Meta:
        unique_together = ('product', 'color', 'size')


class ProductImage(models.Model):
    """Фото привязаны к продукту + цвету — при смене цвета меняются фото"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_main = models.BooleanField(default=False)  # главное фото для этого цвета
    order = models.PositiveIntegerField(default=0) # порядок фото

    def __str__(self):
        return f"{self.product.name} - {self.color.name}"

    class Meta:
        ordering = ['order']