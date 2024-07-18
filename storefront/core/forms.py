from store.models import Customer, Address
from django.contrib.auth import authenticate
from allauth.account.forms import LoginForm
import logging
import us
import os
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from allauth.account.forms import SignupForm
from django import forms
from pathlib import Path
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'password1', 'password2')


class UserDetailForm(forms.Form):
    # Username is typically not editable
    username = forms.CharField(max_length=150, disabled=True)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=150, required=False)


class PasswordResetForm(forms.Form):
    email = forms.EmailField()


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=30, required=False, label='First Name')
    last_name = forms.CharField(
        max_length=30, required=False, label='Last Name')

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        self.send_welcome_email(user)
        return user

    def send_welcome_email(self, user):
        try:
            subject = 'Welcome to MeowMart!'
            message_html = render_to_string(
                'emails/welcome_email.html', {'user': user})
            email = EmailMultiAlternatives(
                subject, '', settings.DEFAULT_FROM_EMAIL, [user.email])
            email.attach_alternative(message_html, "text/html")

            logo_path = Path(settings.BASE_DIR) / 'core/static/core/logo.jpg'
            print(f"BASE_DIR: {settings.BASE_DIR}")
            print(f"Logo path: {logo_path}")

            with open(logo_path, 'rb') as logo_file:
                logo = MIMEImage(logo_file.read())
                logo.add_header('Content-ID', '<logo>')
                email.attach(logo)

            email.send()
        except Exception as e:
            print(f"Error sending email: {e}")


class CustomLoginForm(forms.Form):
    login = forms.CharField(max_length=254)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        login = self.cleaned_data.get('login')
        password = self.cleaned_data.get('password')

        if login and password:
            self.user_cache = authenticate(
                self.request, username=login, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Invalid username/email or password")
        else:
            raise forms.ValidationError(
                "Please enter both username/email and password")
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    current_password = forms.CharField(
        widget=forms.PasswordInput(), required=True, label='Current Password')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'current_password']

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.instance.check_password(current_password):
            raise forms.ValidationError("Current password is incorrect")
        return current_password


class ChangeEmailForm(forms.Form):
    email = forms.EmailField(label='New Email', max_length=254)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['phone']


STATE_CHOICES = [(state.abbr, state.name) for state in us.states.STATES]


class AddressForm(forms.ModelForm):
    state = forms.ChoiceField(
        choices=STATE_CHOICES,
        label='State',
        widget=forms.Select(attrs={
            'class': 'shadow appearance-none border rounded w-full py-2 px-3 leading-tight focus:outline-none focus:shadow-outline custom-select'
        })
    )

    class Meta:
        model = Address
        fields = ['street', 'city', 'state']
