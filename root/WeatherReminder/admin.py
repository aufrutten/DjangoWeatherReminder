from django.contrib import admin

from . import models


@admin.register(models.City)
class CityModel(admin.ModelAdmin):
    readonly_fields = ('_weather', '_humidity', '_last_update', '_temperature')


@admin.register(models.User)
class UserModel(admin.ModelAdmin):
    pass
