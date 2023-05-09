
__all__ = ['router']

from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'citys', views.CityViewSet, basename='city')
router.register(r'users', views.UserViewSet, basename='user')
