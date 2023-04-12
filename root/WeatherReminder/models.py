
from django.db import models
from django.contrib.auth.models import User as DjangoUser
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
