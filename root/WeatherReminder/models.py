
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone


class CityQuerySet(models.query.QuerySet):

    def create(self, **kwargs):
        city_weather_manager = settings.MGR.weather_at_place(kwargs['city']).weather
        kwargs['_temperature'] = city_weather_manager.temperature('celsius')['temp']
        kwargs['_humidity'] = city_weather_manager.humidity
        kwargs['_weather'] = city_weather_manager.detailed_status
        kwargs['_last_update'] = timezone.now()
        return super().create(**kwargs)


class CityManager(models.Manager):

    def get_queryset(self):
        return CityQuerySet(self.model)


class City(models.Model):
    objects = CityManager()

    id = models.BigAutoField(primary_key=True, auto_created=True)
    city = models.CharField(max_length=64, null=False)

    _last_update = models.DateTimeField(auto_now=True)
    _weather = models.CharField(max_length=64, blank=True, null=True)
    _temperature = models.FloatField(blank=True, null=True)
    _humidity = models.FloatField(blank=True, null=True)

    def __str__(self):
        self.update_weather(force_update=False if self._weather else True)
        return f'{self.city}'

    def update_weather(self, force_update=False):
        if timezone.now() >= (self._last_update + settings.FREQUENCY_UPDATE_DATA) or force_update:
            city_weather_manager = settings.MGR.weather_at_place(self.city).weather
            self._temperature = city_weather_manager.temperature('celsius')['temp']
            self._humidity = city_weather_manager.humidity
            self._weather = city_weather_manager.detailed_status
            self._last_update = timezone.now()
            self.save()

    @property
    def temperature(self):
        self.update_weather(force_update=False if self._temperature else True)
        return self._temperature

    @property
    def humidity(self):
        self.update_weather(force_update=False if self._humidity else True)
        return self._humidity

    @property
    def weather(self):
        self.update_weather(force_update=False if self._weather else True)
        return self._weather


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):

        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):

    objects = UserManager()

    username = None
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    subscriptions = models.ManyToManyField("City", blank=True)

    notification_is_enable = models.BooleanField(default=True)
    _frequency_update = models.IntegerField(default=1)
    _latest_notifications = models.DateTimeField(auto_now=True)
    _next_notifications = models.DateTimeField(default=timezone.now() + timedelta(hours=1))

    def __str__(self):
        return f'{self.email}'

    @property
    def latest_notifications(self):
        return self._latest_notifications

    @property
    def next_notifications(self):
        return self._next_notifications

    @property
    def frequency_update(self):
        return self._frequency_update

    @frequency_update.setter
    def frequency_update(self, value):
        if isinstance(value, int):
            self._frequency_update = abs(value)
            self._latest_notifications = timezone.now()
            self._next_notifications = timezone.now() + timedelta(hours=abs(value))
            self.save()
        else:
            raise ValueError("value must be <int>")

    def reset_counter_of_recent_notifications(self):
        if self._frequency_update and self.notification_is_enable:
            self._latest_notifications = timezone.now()
            self._next_notifications = timezone.now() + timedelta(hours=self._frequency_update)
            self.save()
