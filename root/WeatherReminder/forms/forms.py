
__all__ = (
    'SignUpForm',
    'SignInForm',
    'EditProfileForm',
    'SubscriptionsForm',
    'ConfirmEmailForm',
    'AddCityForm',
)

import string
from datetime import date

from django.core.handlers.wsgi import WSGIRequest
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, Reset, Button, HTML, Fieldset, BaseInput, MultiField
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


class SignUpForm(forms.ModelForm):
    first_name = forms.CharField(required=True, min_length=3, max_length=64)
    last_name = forms.CharField(required=True, min_length=3, max_length=64)
    password = custom_fields.ValidatePasswordField(label='Password')
    another_password = custom_fields.PasswordField(label="Confirm password")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'another_password')

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

    def clean_password(self):
        temp_data = self.cleaned_data.copy()
        validate_password(self.data.get('password', ''), User(**temp_data))
        return self.data.get('password', '')

    def clean_another_password(self):
        if self.data.get('password') != self.data.get('another_password'):
            raise ValidationError("Passwords isn't equal")

    def pre_save_data(self):
        data = self.cleaned_data.copy()
        if self.is_valid():
            del data['another_password']
            return data

    def save(self, commit=True):
        data = self.pre_save_data()
        return User.objects.create_user(**data)

    async def async_save(self, commit=True):
        data = self.pre_save_data()
        return await User.objects.acreate_user(**data)


class ConfirmEmailForm(forms.ModelForm):
    code_confirm = forms.CharField(label='Code confirm', required=True)
    delete_account = forms.BooleanField(label='Delete account', required=False, widget=forms.CheckboxInput)

    class Meta:
        model = User
        fields = ('code_confirm',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            FloatingField('code_confirm', css_class='form-floating mb-3'),
            Div('delete_account', wrapper_class='checkbox mb-3'),
        )
        self.helper.add_input(Submit('confirm', 'Confirm', css_class='w-100 mb-2 btn btn-lg rounded-3 btn-primary'))

    def clean_code_confirm(self):
        code_input = self.data.get('code_confirm')
        if code_input and code_input == self.instance.code_confirm:
            return self.instance.code_confirm
        raise ValidationError("Code confirm invalid")

    def save(self, commit=True):
        if self.is_valid():
            self.instance.is_active = True
            return super().save(commit)
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


class SubscriptionsForm(forms.ModelForm):
    subscriptions = forms.ModelMultipleChoiceField(queryset=City.objects.all(),
                                                   widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = User
        fields = ('subscriptions',)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_method = 'post'
        self.helper.layout = Layout()
        self.helper.add_input(Submit('submit', 'Edit', css_class='w-100 mb-2 btn btn-lg rounded-3 btn-primary'))
        super().__init__(*args, **kwargs)


class AddCityForm(forms.Form):

    city = forms.CharField(max_length=128, required=True)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(Field('city', placeholder='Enter'))
        self.helper.add_input(Submit('submit', 'Search', css_class='w-100 mb-2 btn btn-lg rounded-3 btn-primary'))
        super().__init__(*args, **kwargs)

    def clean_city(self):
        if settings.GC.get_cities_by_name(self.data.get('city', '').title()):
            return self.data['city'].title()
        raise ValidationError("That city isn't exist")
