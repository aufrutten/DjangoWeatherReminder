import threading
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from asgiref.sync import sync_to_async, async_to_sync
from . import tools


class CityNotExist(Exception):
    pass


class CityQuerySet(models.query.QuerySet):

    def create(self, **kwargs):
        kwargs['_last_update'] = timezone.now()
        kwargs['city'] = kwargs.get('city', '').title()
        if settings.GC.get_cities_by_name(kwargs['city']):
            return super().create(**kwargs)
        raise CityNotExist(f"city: '{kwargs['city']}' isn't exist")

    def get(self, *args, **kwargs):
        if kwargs.get('city'):
            kwargs['city'] = kwargs.get('city', '').title()
        return super().get(*args, **kwargs)


class CityManager(models.Manager):

    def get_queryset(self):
        return CityQuerySet(self.model)


class City(models.Model):
    objects = CityManager()

    id = models.BigAutoField(primary_key=True, auto_created=True)
    city = models.CharField(max_length=64, null=False, unique=True)

    _last_update = models.DateTimeField(null=True)
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
    def last_update(self):
        self.update_weather(force_update=False if self._last_update else True)
        return self._last_update

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

    @staticmethod
    def message_with_code_confirm(user):
        mail_message = f"Good day! Mr/Miss {user.last_name}\n" \
                       f"Your email: {user.email} has indicated in registration form\n" \
                       f"If it wasn't you don't do nothing\n" \
                       f"\n" \
                       f"Confirm Code: {user.code_confirm}\n" \
                       f"\n" \
                       f"Have a nice day! aufrutten.com"
        return mail_message

    def _create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.code_confirm = tools.generate_code()
        user.latest_notifications = timezone.now()
        user.next_notifications = timezone.now() + timedelta(hours=user.frequency_update)
        user.set_password(password)
        user.is_active = kwargs.get('is_active', False)
        return user

    def create_user(self, email, password=None, **kwargs):
        user = self._create_user(email, password, **kwargs)
        subject, message = 'AufruttenWeatherReminder', self.message_with_code_confirm(user)
        user.email_user(subject=subject, message=message)
        user.save(using=self._db)
        return user

    async def acreate_user(self, email, password=None, **kwargs):
        user = self._create_user(email, password, **kwargs)
        subject, message = 'AufruttenWeatherReminder', self.message_with_code_confirm(user)
        await sync_to_async(user.email_user)(subject=subject, message=message)
        await user.asave(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    objects = UserManager()

    username = None
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    code_confirm = models.CharField(null=True, max_length=6)
    subscriptions = models.ManyToManyField("City", blank=True)

    notification_is_enable = models.BooleanField(default=True)
    frequency_update = models.IntegerField(choices=((1, 1), (3, 3), (6, 6), (12, 12)), default=1, null=False)
    latest_notifications = models.DateTimeField()
    next_notifications = models.DateTimeField()

    def __str__(self):
        return f'{self.email}'

    def __lt__(self, other):
        if not isinstance(other, User):
            raise TypeError('must use Weather.models.User model')
        return self.next_notifications < other.next_notifications

    def email_user(self, subject, message, from_email=None, **kwargs):
        args = {'subject': subject,
                'message': message,
                'from_email': from_email,
                'recipient_list': [self.email],
                **kwargs}
        threading.Thread(target=send_mail, kwargs=args).start()

    async def reset_counter_of_recent_notifications(self):
        if self.frequency_update and self.notification_is_enable:
            self.latest_notifications = timezone.now()
            self.next_notifications = timezone.now() + timedelta(hours=self.frequency_update)
            await self.asave()

    async def send_notifications(self):
        if timezone.now() >= self.next_notifications and await self.subscriptions.afirst() and self.is_active:
            response = await sync_to_async(self.generate_response)()
            await sync_to_async(self.email_user)("DjangoWeatherReminder Notification", response)
        await self.reset_counter_of_recent_notifications()

    def generate_response(self):
        response = []
        for city in self.subscriptions.all():
            response.append(f'{city.city}: weather: {city.weather} temp: {city.temperature}\n')
        return '\n'.join(response)
