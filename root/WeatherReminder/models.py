import threading
from datetime import timedelta
import json

from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.template.loader import render_to_string

from asgiref.sync import sync_to_async, async_to_sync
from rest_framework_simplejwt.tokens import RefreshToken
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from celery import current_app as celery_current_app

from . import tools


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh), str(refresh.access_token)


class CityNotExist(Exception):
    pass


class CityQuerySet(models.query.QuerySet):

    def create(self, **kwargs):
        kwargs['last_update'] = timezone.now()
        kwargs['city'] = kwargs.get('city', '').title().strip()
        if settings.GC.get_cities_by_name(kwargs['city']):
            return super().create(**kwargs)
        raise CityNotExist(f"city: '{kwargs['city']}' isn't exist")

    def get(self, *args, **kwargs):
        if kwargs.get('city'):
            kwargs['city'] = kwargs.get('city', '').title().strip()
        return super().get(*args, **kwargs)


class CityManager(models.Manager):

    def get_queryset(self):
        return CityQuerySet(self.model)


class City(models.Model):
    objects = CityManager()

    id = models.BigAutoField(primary_key=True, auto_created=True)
    city = models.CharField(max_length=64, null=False, unique=True)

    last_update = models.DateTimeField(null=True)
    weather = models.CharField(max_length=64, blank=True, null=True)
    temperature = models.FloatField(blank=True, null=True)
    humidity = models.FloatField(blank=True, null=True)

    def __str__(self):
        self.update_weather(force_update=False if self.weather else True)
        return f'{self.city}'

    def update_weather(self, force_update=False):
        """update weather for city by rules in JSON config of APP"""
        # check diff between last update of that city and now
        # if diff more that rule in my JSON config, do update weather for that city, not for user
        # and that func will trigger when, user get the instance of that city, like in API or in part of UI or Reminder
        if timezone.now() >= (self.last_update + settings.FREQUENCY_UPDATE_DATA) or force_update:
            city_weather_manager = settings.MGR.weather_at_place(self.city).weather
            self.temperature = city_weather_manager.temperature('celsius')['temp']
            self.humidity = city_weather_manager.humidity
            self.weather = city_weather_manager.detailed_status
            self.last_update = timezone.now()
            self.save()


class UserManager(BaseUserManager):

    @staticmethod
    def html_with_code_confirm(user):
        """rendering html for registration form for retrieve code confirm"""
        title = f'Welcome, {user.first_name}'
        text = f"You're receiving this message because you recently signed up for a account." \
               f"<br><br>Confirm your email address by coping confirm code below. " \
               f"This step adds extra security to your business by verifying you own this email." \
               f"<br><br>Confirm code {user.code_confirm}"
        return render_to_string('DWR/email.html', {'message': {'title': title, 'text': text}})

    def _create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.code_confirm = tools.generate_code()
        user.set_password(password)
        user.refresh_token, user.token = get_tokens_for_user(user)
        user.is_active = kwargs.get('is_active', False)
        return user

    def create_user(self, email, password=None, **kwargs):
        user = self._create_user(email, password, **kwargs)
        subject, html_content = 'AufruttenWeatherReminder', self.html_with_code_confirm(user)
        user.email_user(subject=subject, message='', html_message=html_content)
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
    email = models.EmailField(verbose_name="email address", max_length=256, unique=True)
    code_confirm = models.CharField(null=True, max_length=6)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    token = models.CharField(verbose_name='access token', max_length=256)
    refresh_token = models.CharField(verbose_name='refresh token', max_length=256)
    latest_token_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.email}'

    def email_user(self, subject, message, from_email=None, **kwargs):
        """async sending email for user by rewriting the original function"""
        kwargs['subject'] = subject
        kwargs['message'] = message
        kwargs['from_email'] = from_email
        kwargs['recipient_list'] = [self.email]
        celery_current_app.send_task('celery_async_send_email', kwargs)

    def refresh_access_token(self):
        """refresh access token and update refresh token"""
        self.refresh_token, self.token = get_tokens_for_user(self)
        self.latest_token_update = timezone.now()
        self.save()


class Subscription(models.Model):

    user = models.ForeignKey('User', on_delete=models.CASCADE)
    city = models.ForeignKey('City', on_delete=models.CASCADE)
    frequency_update = models.IntegerField(choices=((1, 1), (3, 3), (6, 6), (12, 12)), default=1, null=False)
    task = models.OneToOneField(PeriodicTask, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'city']

    def __str__(self):
        return f'{self.user}:{self.city}'
    
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        with transaction.atomic():
            if self.task:
                self.task.interval.every = self.frequency_update
                self.task.interval.save()
                return super().save(force_insert, force_update, using, update_fields)

            self.task = self.__create_task_func()
            return super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        task = PeriodicTask.objects.filter(name=str(self)).first()
        task.delete()
        super().delete(using, keep_parents)

    def __create_task_func(self):
        schedule = IntervalSchedule.objects.get_or_create(every=self.frequency_update, period=IntervalSchedule.HOURS)[0]
        task = PeriodicTask.objects.get_or_create(name=str(self),
                                                  task='send_notification_to_user',
                                                  interval=schedule,
                                                  start_time=timezone.now(),
                                                  args=json.dumps([self.user.email, self.city.city]))
        task.save()
        return task
