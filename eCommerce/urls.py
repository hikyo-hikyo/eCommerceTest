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
]
