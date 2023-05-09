import string
from random import choice
from functools import wraps

from django.conf import settings
from django.shortcuts import redirect, reverse

from pyowm.commons.exceptions import NotFoundError

from . import models


def generate_code(length=settings.LENGTH_OF_CODE_CONFIRM):
    characters = string.ascii_letters + string.digits
    return ''.join([choice(characters) for _ in range(length)])


def anonymous_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_anonymous:
            return view_func(request, *args, **kwargs)
        return redirect(reverse('home'))
    return wrapper
