"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect, reverse


# <-----ROOT----->
urlpatterns = [path('', lambda request: redirect(reverse('WeatherReminder:root')))]


# <-----ADMIN----->
urlpatterns += [path('admin/', admin.site.urls, name='admin')]


# <-----WeatherReminder----->
urlpatterns += [path('WeatherReminder/', include('WeatherReminder.urls', namespace='WeatherReminder'))]


# <-----SocialDjangoAuthSystem----->
urlpatterns += [path('auth/', include('social_django.urls', namespace='social'))]
