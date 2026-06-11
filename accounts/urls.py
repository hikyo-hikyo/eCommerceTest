
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as account_views

urlpatterns = [
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),
    path('register/', account_views.register, name='register'),


]
