from django.contrib import admin, messages
from django.utils.translation import ngettext

from catalogue.models import (
    Category,
    Brand,
    ProductType,
    Product,
    ProductImage,
    ProductAttribute,
    ProductAttributeValue
)


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    inlines = (ProductAttributeInline,)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = (ProductAttributeValueInline, ProductImageInline)
    list_display = ('upc', 'title', 'product_type', 'quantity', 'category', 'brand', 'is_available')
    list_filter = ('is_available', 'product_type__title')
    list_editable = ('is_available',)
    search_fields = ('upc', 'title', 'description', 'category__name', 'brand__name')
    prepopulated_fields = {'slug': ('title',)}

    actions = ('make_is_available', 'make_is_unavailable')

    @admin.action(description='Available selected products')
    def make_is_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, ngettext(
            '%d story was successfully marked as available.',
            '%d stories were successfully marked as available.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description='Unavailable selected products')
    def make_is_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, ngettext(
            '%d story was successfully marked as unavailable.',
            '%d stories were successfully marked as unavailable.',
            updated,
        ) % updated, messages.SUCCESS)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
