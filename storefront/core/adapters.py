# myapp/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import redirect
from allauth.exceptions import ImmediateHttpResponse
from django.urls import reverse
from django.shortcuts import resolve_url
import logging

logger = logging.getLogger(__name__)

# myapp/adapters.py


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if request.user.is_authenticated:
            return

        if sociallogin.is_existing:
            user = sociallogin.user
            user.backend = 'allauth.account.auth_backends.AuthenticationBackend'
            login(request, user)

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = HttpResponseRedirect(request.GET.get('next') or '/')
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                max_age=3600,  # Token validity in seconds
                samesite='Lax'  # Adjust according to your needs
            )

            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                max_age=3600 * 24 * 7,  # 1 week
                samesite='Lax'
            )

            raise ImmediateHttpResponse(response)

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)

        user.backend = 'allauth.account.auth_backends.AuthenticationBackend'
        login(request, user)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = HttpResponseRedirect(request.GET.get('next') or '/')
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            max_age=3600,  # Token validity in seconds
            samesite='Lax'  # Adjust according to your needs
        )

        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            max_age=3600 * 24 * 7,  # 1 week
            samesite='Lax'
        )

        raise ImmediateHttpResponse(response)

        return user


class MyAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        return reverse("account_confirm_email", args=[emailconfirmation.key])

    def send_mail(self, template_prefix, email, context):
        if template_prefix == 'account/email/password_reset_key':
            context['current_site'] = context.get('current_site', '')
            subject = 'MeowMart Reset Your Password'
            context['email_subject'] = subject
        else:
            subject = None
        msg = self.render_mail(template_prefix, email, context)
        msg.subject = subject
        msg.send()
