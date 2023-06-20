
__all__ = ['urlpatterns']

from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import v1

# Including of versions API
app_name = 'API'
urlpatterns = [
    path(r'token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(r'token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path(r'v1/', include(v1.router.urls), name='V1'),
]
