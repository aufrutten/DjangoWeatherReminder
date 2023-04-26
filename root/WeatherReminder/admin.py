from django.contrib import admin

from . import models
from . import forms


@admin.register(models.City)
class CityModel(admin.ModelAdmin):
    pass


@admin.register(models.User)
class UserModel(admin.ModelAdmin):
    pass
