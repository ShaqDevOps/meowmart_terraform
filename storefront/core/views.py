# Adjust the import based on your actual model location
from django.shortcuts import render
from decimal import Decimal
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
import logging
import json
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views import View
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.models import SocialAccount
from allauth.account.auth_backends import AuthenticationBackend
from allauth.account.forms import SignupForm
from django.urls import reverse
from .forms import CustomUserCreationForm, CustomLoginForm, UserUpdateForm, ChangeEmailForm
from .serializers import UserCreateSerializer, UserSerializer
from store.models import Customer, Address
from .forms import UserForm, CustomerForm, AddressForm
from store.models import Customer, Address

User = get_user_model()
logger = logging.getLogger('core')

User = get_user_model()


class SignUpViewSet(ModelViewSet):
    serializer_class = UserCreateSerializer

    def get_queryset(self):
        if self.action == 'list':
            return User.objects.none()
        return super().get_queryset()

    def get_permissions(self):
        if self.request.method in ['GET', 'POST']:
            return [AllowAny()]
        else:
            return [IsAdminUser()]

    @action(detail=False, methods=['get', 'post'])
    def SignUpForm(self, request):
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.email = form.cleaned_data['email']
                user.save()

                # Specify the backend when logging in the user
                backend = 'allauth.account.auth_backends.AuthenticationBackend'
                user.backend = backend

                login(request, user, backend=backend)
                return redirect('/')
        else:
            form = CustomUserCreationForm()

        return render(request, 'account/signup.html', {'form': form})


class CustomLoginView(View):
    template_name = "account/login.html"

    def get(self, request):
        form = CustomLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CustomLoginForm(request.POST, request=request)
        if form.is_valid():
            user = form.get_user()
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
            return response
        else:
            messages.error(request, 'Invalid username/email or password')
            return render(request, self.template_name, {'form': form})


@permission_classes([AllowAny])
class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        elif user.is_authenticated:
            return User.objects.filter(id=user.id)

    @action(detail=False, methods=['GET', 'PATCH'])
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            print(serializer.data)
            return Response(serializer.data)


# @login_required
# def my_profile(request):
#     token = request.COOKIES.get('access_token')
#     if not token:
#         return redirect(f'/accounts/login/?next={request.path}')
#     return render(request, 'core/my_profile.html')


def change_password(request):
    return redirect('/accounts/password/reset/')


logger = logging.getLogger(__name__)


@login_required
def custom_logout(request):
    response = HttpResponseRedirect('/')

    # Delete cookies
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    response.delete_cookie('sessionid')
    response.delete_cookie('csrftoken')

    try:
        auth_logout(request)

        if SocialAccount.objects.filter(user=request.user).exists():
            return redirect('/accounts/logout/')
    except AttributeError:
        pass
    except Exception as e:
        pass

    return response


def change_details(request):
    user = request.user
    customer, created = Customer.objects.get_or_create(user=user)
    address, created = Address.objects.get_or_create(customer=customer)

    if request.method == 'POST':
        post_data = request.POST.copy()
        # Ensure the email field is populated with the user's current email if not provided
        if 'email' not in post_data:
            post_data['email'] = user.email

        user_form = UserForm(post_data, instance=user)
        customer_form = CustomerForm(request.POST, instance=customer)
        address_form = AddressForm(request.POST, instance=address)

        if user_form.is_valid() and customer_form.is_valid() and address_form.is_valid():
            user_form.save()
            customer_form.save()
            address_form.save()
            return redirect('core:my_info')
    else:
        user_form = UserForm(instance=user)
        customer_form = CustomerForm(instance=customer)
        address_form = AddressForm(instance=address)

    context = {
        'user_form': user_form,
        'customer_form': customer_form,
        'address_form': address_form,
        'user': user,
        'customer': customer,
        'address': address,
    }

    return render(request, 'core/change_details.html', context)


def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            request.user.email = form.cleaned_data['email']
            request.user.save()
            return redirect('core:my_info')
    else:
        form = ChangeEmailForm()
        return render(request, 'core/change_email.html', {'form': form})


def confirm_password(request):
    # Default to 'change_details' if no next URL is provided
    next_url = request.GET.get('next', 'change_details')
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        if user:
            # Log the user in after successful authentication
            login(request, user)
            return redirect(next_url)  # Redirect to the next URL
        else:
            return render(request, 'core/confirm_password.html', {'error': 'Incorrect password', 'next': next_url})
    return render(request, 'core/confirm_password.html', {'next': next_url})


@login_required
def profile(request):
    return render(request, 'core/profile.html')


def my_info(request):
    user = request.user
    customer, created = Customer.objects.get_or_create(user=user)
    address, created = Address.objects.get_or_create(customer=customer)

    context = {
        'user': user,
        'customer': customer,
        'address': address,
    }

    return render(request, 'core/my_info.html', context)


def my_orders(request):
    user = request.user

    user_orders = user.customer.order_set.all()
    orders_with_totals = []
    for order in user_orders:
        print(f"Processing Order ID: {order.id}")
        items_with_totals = []
        order_total = 0
        for item in order.items.all():
            total_price = item.quantity * item.unit_price
            order_total += total_price
            items_with_totals.append({
                'product': item.product,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total_price': total_price,
            })
        orders_with_totals.append({
            'order': order,
            'items': items_with_totals,
            'order_total': order_total,
        })
    context = {
        'orders_with_totals': orders_with_totals,
    }

    return render(request, 'core/my_orders.html', context)


def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')
