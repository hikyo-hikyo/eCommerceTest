# eCommerce/admin.py
from django.contrib import admin
from .models import Store, Product, Cart, Cart_Item, Review

# Vendor + Product Management


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'created_at']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'store', 'price', 'stock', 'is_active']
    list_filter = ['is_active', 'store']
    search_fields = ['name', 'description']
    raw_id_fields = ['store']


# Optional: Cart & Reviews
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'created_at']


@admin.register(Cart_Item)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'buyer', 'rating', 'created_at']
