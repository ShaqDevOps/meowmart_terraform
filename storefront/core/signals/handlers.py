from urllib.parse import urlparse, parse_qs
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import logging
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.account.signals import user_logged_in
from django.dispatch import receiver
from store.signals import order_created


@receiver(order_created)
def on_order_created(sender, **kwargs):
    print(kwargs['order'])


# core/signals/handler.py


# @receiver(user_logged_in)
# def create_jwt_token(sender, request, user, **kwargs):
#     print("Signal received: user_logged_in")
#     refresh = RefreshToken.for_user(user)
#     access_token = str(refresh.access_token)

#     print(f"Generated Access Token: {access_token}")

#     request.session['access_token'] = access_token
#     request.session['refresh_token'] = str(refresh)

#     response = HttpResponse("Logged in successfully")
#     response.set_cookie(
#         key='access_token',
#         value=access_token,
#         httponly=True,
#         max_age=3600,
#         samesite='Lax'
#     )
#     response.set_cookie(
#         key='refresh_token',
#         value=str(refresh),
#         httponly=True,
#         max_age=3600 * 24 * 7,
#         samesite='Lax'
#     )

#     request._response = response
#     print("Cookies set successfully")


@receiver(user_logged_in)
def create_jwt_token(sender, request, user, **kwargs):
    print("Signal received: user_logged_in")
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    print(f"Generated Access Token: {access_token}")

    request.session['access_token'] = access_token
    request.session['refresh_token'] = str(refresh)

    # Determine the next URL to redirect to
    parsed_url = urlparse(request.META.get('HTTP_REFERER', '/'))
    query_params = parse_qs(parsed_url.query)
    next_url = query_params.get('next', ['/'])[0]

    response = HttpResponseRedirect(next_url)
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        max_age=3600,
        samesite='Lax'
    )
    response.set_cookie(
        key='refresh_token',
        value=str(refresh),
        httponly=True,
        max_age=3600 * 24 * 7,
        samesite='Lax'
    )

    request._response = response
    print("Cookies set successfully")
