from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Main apps
    path('', include('grabsomore.urls')),
    path('shop/', include('eCommerce.urls', namespace='ecommerce')),
    path('accounts/', include('accounts.urls')),

    # API
    path('api/', include('eCommerce.api_urls', namespace='ecommerce-api')),
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),

    # JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
