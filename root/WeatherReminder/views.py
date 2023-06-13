import asyncio
from datetime import timedelta

from django.shortcuts import render, reverse, redirect, get_object_or_404, HttpResponse, get_list_or_404
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from asgiref.sync import sync_to_async, async_to_sync
from django.utils import timezone

from . import forms
from . import tools
from . import models


@login_required
def get_token(request: WSGIRequest):
    if request.method == "POST" and (request.POST.get('refresh_token') == request.user.refresh_token):
        request.user.refresh_access_token()
    return render(request, 'DWR/token.html', context={'form': forms.TokenRefreshForm(instance=request.user)})


@login_required
def add_city(request: WSGIRequest):
    if request.method == "POST":
        form = forms.AddCityForm(request.POST)
        if form.is_valid():
            return redirect(reverse('WeatherReminder:city', args=[form.cleaned_data['city']]))
        return render(request, 'DWR/add_city.html', context={'form': form})
    return render(request, 'DWR/add_city.html', context={'form': forms.AddCityForm()})


@login_required
def city(request: WSGIRequest, city_name):
    city_obj = models.City.objects.get_or_create(city=city_name)[0]
    city_obj.update_weather(force_update=False if city_obj.temperature else True)
    instance_record = models.Subscription.objects.filter(user=request.user, city=city_obj).first()
    if request.method == "POST":
        instance_record = models.Subscription.objects.get_or_create(user=request.user, city=city_obj)[0]
        form = forms.SubscriptionsForm(request.POST, instance=instance_record)
        if form.is_valid():
            form.save()
    form = forms.SubscriptionsForm(instance=instance_record)
    return render(request, 'DWR/city.html', context={"city": city_obj, 'form': form})


@login_required
def unsubscribe(request: WSGIRequest, city_name):
    city_obj = models.City.objects.get_or_create(city=city_name)[0]
    subscription_record = models.Subscription.objects.filter(city=city_obj, user=request.user).first()
    if subscription_record:
        subscription_record.delete()
    return redirect(reverse('WeatherReminder:home'))


@login_required
def profile(request: WSGIRequest):
    if request.method == "POST":
        form = forms.EditProfileForm(request.POST, instance=request.user)
        if not form.is_valid():
            return render(request, 'DWR/profile.html', context={'form': form})
        form.save()
    return render(request, 'DWR/profile.html', context={'form': forms.EditProfileForm(instance=request.user)})


@login_required
def home(request: WSGIRequest):
    subscriptions_list = models.Subscription.objects.filter(user=request.user).all()
    return render(request, 'DWR/home.html', context={'subscriptions': subscriptions_list})


@tools.anonymous_required
def login(request: WSGIRequest):
    if request.method == "POST":
        form = forms.SignInForm(request.POST)

        if not form.is_valid():
            return render(request, 'DWR/login.html', status=401, context={'form': form})

        if not form.user.is_active:
            return redirect(reverse('WeatherReminder:confirm_email', args=[form.cleaned_data['email']]))

        user_auth = authenticate(request, email=form.cleaned_data['email'], password=form.cleaned_data.get('password'))
        auth_login(request, user_auth)

        return redirect(reverse('WeatherReminder:home'))

    return render(request, 'DWR/login.html', status=401, context={'form': forms.SignInForm()})


@tools.anonymous_required
def email_confirm(request: WSGIRequest, email):
    if request.method == "POST":
        user = get_object_or_404(models.User, email=email)

        if user.is_active:
            return redirect(reverse('WeatherReminder:login'))

        form = forms.ConfirmEmailForm(request.POST, instance=user)

        if not form.is_valid():
            return render(request, 'DWR/email_confirm.html', context={'email': user.email, 'form': form})

        if form.cleaned_data.get('delete_account'):
            user.delete()
            return redirect(reverse('WeatherReminder:register'))

        form.save()
        return redirect(reverse('WeatherReminder:login'))
    return render(request, 'DWR/email_confirm.html', context={'email': email, 'form': forms.ConfirmEmailForm()})


@tools.anonymous_required
def register(request):
    if request.method == "POST":
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('WeatherReminder:confirm_email', args=[form.cleaned_data.get('email')]))
        return render(request, 'DWR/register.html', context={'form': form})
    return render(request, 'DWR/register.html', context={'form': forms.SignUpForm()})
