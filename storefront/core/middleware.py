from django.urls import reverse
import requests
from django.conf import settings
from django.shortcuts import redirect
import logging
from django.utils.deprecation import MiddlewareMixin
import os
from django.contrib.auth.middleware import get_user
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.state import token_backend


# storefront/core/middleware.py
from django.shortcuts import redirect
from django.conf import settings
import requests


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_authentication = JWTAuthentication()

    def __call__(self, request):
        try:
            # Extract the token from the Authorization header
            header = self.jwt_authentication.get_header(request)
            if header:
                raw_token = header.split()[1] if len(
                    header.split()) > 1 else header
                validated_token = self.jwt_authentication.get_validated_token(
                    raw_token)
                request.user = self.jwt_authentication.get_user(
                    validated_token)
            else:
                # Get the token from the cookies if not in header
                cookie = request.COOKIES.get('access_token')
                session_token = request.session.get('access_token')
                if cookie:
                    validated_token = self.jwt_authentication.get_validated_token(
                        cookie)
                    request.user = self.jwt_authentication.get_user(
                        validated_token)
                elif session_token:
                    validated_token = self.jwt_authentication.get_validated_token(
                        session_token)
                    request.user = self.jwt_authentication.get_user(
                        validated_token)
                else:
                    request.user = AnonymousUser()
        except (InvalidToken, TokenError) as e:
            print(f"Error processing token: {e}")
            request.user = AnonymousUser()

        response = self.get_response(request)

        # If the response is set by the signal, use it
        if hasattr(request, '_response'):
            response = request._response

        return response


# middleware.py

class RefreshJWTTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')

        if not access_token and refresh_token:
            # Use reverse to get the URL for the refresh token endpoint
            try:
                refresh_token_endpoint = request.build_absolute_uri(
                    reverse('jwt-refresh'))
                # Attempt to get a new access token using the refresh token
                response = requests.post(refresh_token_endpoint, json={
                    'refresh': refresh_token
                })
            except requests.exceptions.RequestException as e:
                print(f"Error during request to refresh token: {e}")
                return redirect(f'/accounts/login/?next={request.path}')

            if response.status_code == 200:
                new_access_token = response.json().get('access')
                # Update the request's cookies with the new access token
                response = self.get_response(request)
                response.set_cookie('access_token', new_access_token)
                return response
            else:
                return redirect(f'/accounts/login/?next={request.path}')

        response = self.get_response(request)
        return response
