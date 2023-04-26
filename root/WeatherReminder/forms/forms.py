
__all__ = ('SignUpForm', 'SignInForm', 'EditProfileForm', 'NewCitySubscribe', 'ConfirmEmailForm')

import string
from datetime import date

from django.core.handlers.wsgi import WSGIRequest
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, Reset, Button, HTML, Fieldset, BaseInput
from crispy_forms.bootstrap import PrependedText, PrependedAppendedText, FormActions, AccordionGroup, Modal
from crispy_bootstrap5.bootstrap5 import FloatingField, Field

from . import fields as custom_fields
from ..models import User, City
from .. import tools


class SignInForm(forms.Form):
    email = custom_fields.EmailField(label='Email address')
    password = custom_fields.PasswordField(label='Password')
    remember_me = forms.BooleanField(label='Remember me',
                                     required=False,
                                     widget=forms.CheckboxInput)

    def __init__(self, *args, **kwargs):
        self.user = None
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            FloatingField('email', css_class='form-floating mb-3'),
            FloatingField('password', css_class='form-floating mb-3'),
            Div('remember_me', wrapper_class='checkbox mb-3'),
            Submit('submit', 'Sing up', css_class='w-100 mb-2 btn btn-lg rounded-3 btn-primary')
        )

        super().__init__(*args, **kwargs)

    def clean_email(self):
        if User.objects.filter(email=self.data.get('email', '').lower()).exists():
            return self.data['email'].lower()
        raise ValidationError('Email is not exist')

    def clean_password(self):
        user = User.objects.filter(email=self.data.get('email', '').lower()).first()
        if user and user.check_password(self.data.get('password')):
            self.user = user
            return self.data['password']
        raise ValidationError("Password isn't correct")


class SignUpForm(forms.Form):
    first_name = forms.CharField(label='First name',
                                 required=True,
                                 min_length=3,
                                 max_length=64)

    last_name = forms.CharField(label='Last name',
                                required=True,
                                min_length=3,
                                max_length=64)

    email = custom_fields.EmailField(label='Email address')
    password = custom_fields.ValidatePasswordField(label='Password')
    another_password = custom_fields.PasswordField(label="Confirm password")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            FloatingField('first_name', css_class='form-floating mb-3'),
            FloatingField('last_name', css_class='form-floating mb-3'),
            FloatingField('email', css_class='form-floating mb-3'),
            FloatingField('password', css_class='form-floating mb-3'),
            FloatingField('another_password', css_class='form-floating mb-3'),
        )
        self.helper.add_input(Submit('submit', 'Sing up', css_class='w-100 mb-2 btn btn-lg rounded-3 btn-primary'))

    def clean_email(self):
        if User.objects.filter(email=self.data.get('email', '').lower()).exists():
            raise ValidationError("Email has been exist")
        return self.data['email']

    def clean_password(self):
        validate_password(self.data.get('password', ''))
        return self.data.get('password', '')

    def clean_another_password(self):
        if self.data.get('password') != self.data.get('another_password'):
            raise ValidationError("Passwords isn't equal")

    def save(self):
        if self.is_valid():
            return User.objects.create_user(self.cleaned_data['email'],
                                            self.cleaned_data['password'])


class ConfirmEmailForm(forms.Form):
    code = forms.CharField(min_length=settings.LENGTH_OF_CODE_CONFIRM,
                           max_length=settings.LENGTH_OF_CODE_CONFIRM,
                           required=True,
                           label='Code confirm')

    delete_account = forms.BooleanField(label='Delete account',
                                        required=False,
                                        widget=forms.CheckboxInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._code_compare = ''

        self.helper = FormHelper()

        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            FloatingField('code', css_class='form-floating mb-3'),
            Div('delete_account', wrapper_class='checkbox mb-3'),
        )

        self.helper.add_input(Submit('confirm', 'Confirm', css_class='w-100 mb-2 btn btn-lg rounded-3 btn-primary'))

    @property
    def code_compare(self):
        if self._code_compare:
            return self._code_compare
        raise ValueError('Attribute <code_compare> not set')

    @code_compare.setter
    def code_compare(self, value):
        if not isinstance(value, str):
            raise TypeError('Invalid type, request must be <str>')
        self._code_compare = value

    def clean_code(self):
        if self.data.get('code') == self.code_compare:
            return self.data['code']
        raise ValidationError("Code confirm invalid")


class EditProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'notification_is_enable', 'frequency_update')

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
                PrependedText('first_name', 'Name'),
                PrependedText('last_name', 'Surname'),

                PrependedText('notification_is_enable', 'Notification'),
                PrependedText('frequency_update', 'Frequency'),
        )

        self.helper.add_input(Submit('submit', 'Edit', css_class='w-100 mb-2 btn btn-lg rounded-3 btn-primary'))
        super().__init__(*args, **kwargs)


class NewCitySubscribe(forms.Form):
    city = None


