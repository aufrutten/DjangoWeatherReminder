
__all__ = ['urlpatterns']

from django.urls import path, include

from . import v1

# Including of versions API
urlpatterns = [
    path(r'v1/', include(v1.router.urls), name='api_v1'),
]
