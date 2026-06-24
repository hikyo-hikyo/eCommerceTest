# eCommerce/admin.py
from django.contrib import admin
from .models import Store, Product, Cart, Cart_Item, Review, Order, Order_Item

# Vendor + Product Management

"""These are all admin views for the eCommerce app. It lists all the info for the products, stores, and reviews."""


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'created_at']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'store', 'price', 'stock', 'is_active']
    list_filter = ['is_active', 'store']
    search_fields = ['name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'buyer', 'rating', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'rating']
    search_fields = ['product__name', 'buyer__username', 'comment']
    raw_id_fields = ['product', 'buyer']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'created_at']


@admin.register(Cart_Item)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'order_date', 'total_amount']


@admin.register(Order_Item)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity']
