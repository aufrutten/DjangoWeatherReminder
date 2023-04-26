
from django import forms
from django.core.exceptions import ValidationError

from ..models import User


class EmailField(forms.EmailField):

    def __init__(self, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 128)
        kwargs['required'] = kwargs.get('required', True)
        kwargs['widget'] = kwargs.get('widget', forms.EmailInput)
        super().__init__(**kwargs)


class PasswordField(forms.CharField):
    def __init__(self, **kwargs):
        kwargs['required'] = kwargs.get('required', True)
        kwargs['max_length'] = kwargs.get('max_length', 64)
        kwargs['min_length'] = kwargs.get('min_length', 4)
        kwargs['widget'] = forms.PasswordInput
        super().__init__(**kwargs)


class ValidatePasswordField(PasswordField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def validate(self, value: str):
        if not any(char.islower() for char in value):
            raise ValidationError("Password doesn't have any lower character")

        if not any(char.isupper() for char in value):
            raise ValidationError("Password doesn't have any upper character")

        if not any(char.isdigit() for char in value):
            raise ValidationError("Password doesn't have any digit character")
