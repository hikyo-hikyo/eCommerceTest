from django.urls import path
from . import views


app_name = 'grabsomore'

urlpatterns = [

    path('', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),

    # Password reset URLs (keep these)
    path('request_password_reset/', views.send_password_reset,
         name='request_password_reset'),
    path('reset_password/<str:token>/',
         views.reset_user_password, name='reset_user_password'),
    path('reset_password/', views.reset_password, name='reset_password'),
]
