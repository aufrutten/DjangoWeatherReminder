from django.urls import path
from django.shortcuts import redirect, reverse
from django.contrib.auth import logout as auth_logout
from . import views


def root(request):
    return redirect(reverse('home'))


def logout(request):
    auth_logout(request)
    return redirect(reverse('login'))


def handler404(request, exception):
    return render(request, 'base/404.html', status=404)


urlpatterns = [
    path('', root, name='root'),

    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', logout, name='logout'),
    path('confirm_email/<str:email>', views.email_confirm, name='confirm_email'),

    path('home/', views.home, name='home'),
    path('profile/', views.profile, name='profile'),

    path('city/', views.add_city, name='add_city'),
    path('city/<str:city_name>', views.city, name="city"),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
]
