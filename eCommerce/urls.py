from django.urls import path
from . import views

app_name = 'eCommerce'  # This helps Django know these URLs belong to the eCommerce app

urlpatterns = [
    # Home page: Shows the list of all products
    path('', views.list_products, name='products_list'),

    # Page to view details about a specific product (with a search form)
    path('product/', views.view_product_page, name='product_page'),

    # Page to change the price of a product (for users with permission)
    path('change-price/', views.change_product_price, name='change_price'),

    # URL to add an item to the shopping cart (usually called by a form)
    path('add-to-cart/', views.add_item_to_cart, name='add_to_cart'),

    # Page showing all items currently in the user's cart with totals
    path('cart/', views.show_user_cart, name='main_cart_page'),

    # URL to clear all items from the user's cart
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    # Vendor URLs
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
    path('buyer/home/', views.buyer_home, name='buyer_home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/',
         views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='main_cart_page'),
    path('cart/remove/<int:item_id>/',
         views.remove_from_cart, name='remove_from_cart'),
]
