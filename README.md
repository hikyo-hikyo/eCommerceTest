# eCommerce Marketplace

A full-featured Django-based eCommerce platform where vendors can create stores and list products, and customers can browse, review, and add items to their cart.

Built with **Django**, **Django REST Framework (DRF)**, and custom user authentication.

---

## Features

### For Vendors
- Create and manage their own Store
- Add, edit, and manage Products (with stock, images, and activation status)
- View their store's performance

### For Customers
- Browse all stores and products
- View detailed product information with reviews
- Add products to cart
- Leave reviews on purchased products (one review per product)

### Technical Features
- **REST API** with ViewSets for Stores, Products, and Reviews
- Custom user model with extended functionality
- Proper permissions (vendors can only manage their own stores/products)
- Responsive Django templates
- Cart system with unique items per cart
- Order management (basic structure included)

---

## Tech Stack

- **Backend**: Django 4+
- **API**: Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (recommended for production)
- **Authentication**: Custom User model + Django's auth system
- **Frontend**: Django Templates + HTML/CSS

---

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/hikyo-hikyo/eCommerceTest.git
cd eCommerceTest