from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from . import models

# @admin.register(models.User)
# class UserAdmin(DefaultUserAdmin):
#     pass

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'in_stock', 'category', 'new_price', 'old_price')
    list_filter = ('active', 'in_stock', 'date_updated')
    list_editable = ('in_stock', 'old_price', 'new_price',)
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
admin.site.register(models.Product, ProductAdmin)

class ProductTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
admin.site.register(models.ProductTag, ProductTagAdmin)

class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ('products',)
admin.site.register(models.Category, ProductTagAdmin)

class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_tag', 'product_name')
    readonly_fields = ('thumbnail',)
    search_fields = ('product__name',)
    def thumbnail_tag(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="%s"/>' % obj.thumbnail.url
            )
        return "-"
    thumbnail_tag.short_description = "Thumbnail"
    def product_name(self, obj):
        return obj.product.name
admin.site.register(models.ProductImage, ProductImageAdmin)