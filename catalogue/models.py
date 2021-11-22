from django.db import models

from catalogue.manager import ProductManager


class ProductType(models.Model):
    title = models.CharField(max_length=32, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ProductAttribute(models.Model):
    INTEGER = 1
    STRING = 2
    FLOAT = 3

    ATTRIBUTE_TYPE_CHOICES = (
        (INTEGER, 'Integer'),
        (STRING, 'String'),
        (FLOAT, 'Float')
    )

    title = models.CharField(max_length=32)
    product_type = models.ForeignKey(
        to=ProductType,
        on_delete=models.CASCADE,
        related_name='attributes'
    )
    attribute_type = models.PositiveSmallIntegerField(
        choices=ATTRIBUTE_TYPE_CHOICES,
        default=INTEGER
    )

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'[{self.product_type}] - {self.title}'


class Category(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=32, unique=True)
    parent = models.ForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True
    )

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse(viewname='catalogue:category-product-list', kwargs={'pk': self.pk, 'slug': self.slug})

    @property
    def get_children_category(self):
        children = list(self.children.all())
        yield self
        for child in children:
            for _ in child.get_children_category:
                yield _


class Brand(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=32, unique=True)
    parent = models.ForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True
    )

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    product_type = models.ForeignKey(
        to=ProductType,
        on_delete=models.PROTECT,
        related_name='products'
    )
    upc = models.BigIntegerField(unique=True)
    title = models.CharField(max_length=32)
    slug = models.SlugField(max_length=32, unique=True)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    quantity = models.PositiveSmallIntegerField(default=10)
    category = models.ForeignKey(
        to=Category,
        on_delete=models.PROTECT,
        related_name='products'
    )
    brand = models.ForeignKey(
        to=Brand,
        on_delete=models.PROTECT,
        related_name='products'
    )

    objects = ProductManager()

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'[{self.product_type}] - {self.title}'

    @property
    def get_stock(self):
        return self.partners.order_by('price').first()

    @property
    def get_stocks(self):
        return self.partners.prefetch_related('partner').exclude(partner_id=self.get_stock.partner.pk).order_by('price')

    @property
    def get_attributes(self):
        return self.attribute_values.all()

    @property
    def get_images(self):
        return self.images.all()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse(viewname='catalogue:product-detail', kwargs={'pk': self.pk, 'slug': self.slug})

    @property
    def get_category_list(self):
        category = self.category

        category_list = []
        while category is not None:
            category_list.append(category)
            category = category.parent
        return category_list


class ProductImage(models.Model):
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f'{self.product}'


class ProductAttributeValue(models.Model):
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name='attribute_values'
    )
    product_attribute = models.ForeignKey(
        to=ProductAttribute,
        on_delete=models.PROTECT,
        related_name='attribute_values'
    )
    value = models.CharField(max_length=48)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'[{self.product}] - {self.product_attribute.title} : {self.value}'
