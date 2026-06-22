from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views_api import StoreViewSet, ProductViewSet, ReviewViewSet

app_name = 'eCommerce'


urlpatterns = [
    # Regular Web Views (Buyer + Vendor)
    path('buyer/home/', views.buyer_home, name='buyer_home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/',
         views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='main_cart_page'),
    path('cart/remove/<int:item_id>/',
         views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('catalog/', views.product_catalog, name='product_catalog'),
    path('store/<int:store_id>/', views.store_detail, name='store_detail'),

    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/store/create/', views.create_store, name='create_store'),
    path('vendor/store/<int:store_id>/edit/',
         views.edit_store, name='edit_store'),
    path('vendor/store/<int:store_id>/delete/',
         views.delete_store, name='delete_store'),
    path('vendor/store/<int:store_id>/products/',
         views.vendor_store_products, name='vendor_store_products'),
    path('vendor/store/<int:store_id>/product/add/',
         views.add_product, name='add_product'),

    path('reddit/', views.reddit_feed, name='reddit_feed'),


]
