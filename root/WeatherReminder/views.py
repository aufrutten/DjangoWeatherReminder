import asyncio

from django.shortcuts import render, reverse, redirect, get_object_or_404, HttpResponse
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from asgiref.sync import sync_to_async

from . import forms
from . import tools
from . import models


@login_required
def subscriptions(request: WSGIRequest):
    if request.method == "POST":
        form = forms.SubscriptionsForm(request.POST, instance=request.user)
        if not form.is_valid():
            return render(request, 'DWR/subscriptions.html.html', context={'form': form})
        form.save()
        return redirect(reverse('home'))
    return render(request, 'DWR/subscriptions.html', context={'form': forms.SubscriptionsForm(instance=request.user)})


@login_required
def add_city(request: WSGIRequest):
    if request.method == "POST":
        form = forms.AddCityForm(request.POST)
        if form.is_valid():
            return redirect(reverse('city', args=[form.cleaned_data['city']]))
        return render(request, 'DWR/add_city.html', context={'form': form})
    return render(request, 'DWR/add_city.html', context={'form': forms.AddCityForm()})


@login_required
def city(request: WSGIRequest, city_name):
    city_obj = models.City.objects.get_or_create(city=city_name)[0]
    return render(request, 'DWR/city.html', context={"city": city_obj})


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
    subscriptions_list = get_object_or_404(models.User, email=request.user).subscriptions.all()
    return render(request, 'DWR/home.html', context={'subscriptions': subscriptions_list})


@tools.anonymous_required
def login(request: WSGIRequest):
    if request.method == "POST":
        form = forms.SignInForm(request.POST)

        if not form.is_valid():
            return render(request, 'DWR/login.html', status=401, context={'form': form})

        if not form.user.is_active:
            return redirect(reverse('confirm_email', args=[form.cleaned_data['email']]))

        user_auth = authenticate(request, email=form.cleaned_data['email'], password=form.cleaned_data.get('password'))
        auth_login(request, user_auth)

        return redirect(reverse('home'))

    return render(request, 'DWR/login.html', status=401, context={'form': forms.SignInForm()})


@tools.anonymous_required
def email_confirm(request: WSGIRequest, email):
    user = get_object_or_404(models.User, email=email)

    if user.is_active:
        return redirect(reverse('login'))

    if request.method == "POST":
        form = forms.ConfirmEmailForm(request.POST, instance=user)

        if not form.is_valid():
            return render(request, 'DWR/email_confirm.html', context={'email': user.email, 'form': form})

        if form.cleaned_data.get('delete_account'):
            user.delete()
            return redirect(reverse('register'))

        form.save()
        return redirect(reverse('login'))
    return render(request, 'DWR/email_confirm.html', context={'email': user.email, 'form': forms.ConfirmEmailForm()})


@tools.anonymous_required
def register(request):
    if request.method == "POST":
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            asyncio.run(form.async_save())
            return redirect(reverse('confirm_email', args=[form.cleaned_data.get('email')]))
        return render(request, 'DWR/register.html', context={'form': form})
    return render(request, 'DWR/register.html', context={'form': forms.SignUpForm()})
