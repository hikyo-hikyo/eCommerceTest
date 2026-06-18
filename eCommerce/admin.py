# eCommerce/admin.py
from django.contrib import admin
from .models import Store, Product, Cart, Cart_Item, Review

# Vendor + Product Management


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'created_at', 'product_count']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    raw_id_fields = ['vendor']

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'store', 'price',
                    'stock', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'store']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock', 'is_active']
    raw_id_fields = ['store']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['comment', 'product__name', 'user__username']
    raw_id_fields = ['product', 'user']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'created_at']


@admin.register(Cart_Item)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity']


'''@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['comment']'''
