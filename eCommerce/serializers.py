from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Store, Product, Review

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(
        source='user.username')

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'price',
            'description',
            'stock',
            'store',
            'store_name',
            'reviews',
            'created_at'
        ]
        read_only_fields = ['created_at']


class StoreSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    vendor_username = serializers.CharField(
        source='vendor.username', read_only=True)

    class Meta:
        model = Store
        fields = [
            'id',
            'name',
            'description',
            'vendor',
            'vendor_username',
            'products',
            'created_at'
        ]
        read_only_fields = ['vendor', 'created_at', 'vendor_username']
