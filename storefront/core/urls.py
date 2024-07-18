
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import TemplateView


app_name = 'core'

router = DefaultRouter()
router.register('SignUp', views.SignUpViewSet, basename='SignUp')
router.register('user', views.UserViewSet, basename='user')

# URLConf
urlpatterns = [
    path('', TemplateView.as_view(template_name='core/index.html'), name='Home'),
    #     path('signin/', views.SignIn, name='sign-in'),
    # path('profile/', views.my_profile, name='customer-profile')
    path('profile/', views.profile, name='profile'),
    path('profile/my_info/', views.my_info, name='my_info'),
    path('profile/my_orders/', views.my_orders, name='my_orders'),
    path('profile/change_details', views.change_details, name='change_details'),
    path('profile/change_email/', views.change_email, name='change_email'),
    path('profile/confirm_password/',
         views.confirm_password, name='confirm_password'),
    path('change_password/', views.change_password, name='change_password'),
    path('logout/', views.custom_logout, name='logout'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('accounts/login', views.CustomLoginView.as_view(), name='custom_login')
]

urlpatterns += router.urls
