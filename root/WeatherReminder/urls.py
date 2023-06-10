from django.urls import path, include
from django.shortcuts import redirect, reverse
from django.contrib.auth import logout as auth_logout
from rest_framework_simplejwt import views as jwt_views
from . import API
from . import views

app_name = 'WeatherReminder'


def root(request):
    return redirect(reverse('WeatherReminder:home'))


def logout(request):
    auth_logout(request)
    return redirect(reverse('WeatherReminder:login'))


def handler404(request, exception):
    return render(request, 'base/404.html', status=404)


urlpatterns = [
    path('', root, name='root'),

    path('api-auth/', include('rest_framework.urls', namespace='APIAuth')),
    path('api/', include(API.urls, namespace='API')),

    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', logout, name='logout'),
    path('confirm_email/<str:email>', views.email_confirm, name='confirm_email'),

    path('home/', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('token/', views.get_token, name='token'),

    path('city/', views.add_city, name='add_city'),
    path('city/<str:city_name>', views.city, name="city"),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
]
