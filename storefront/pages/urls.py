
from django.urls import path, include
from . import views

app_name = 'pages'
urlpatterns = [


    path('faq', views.faq_view, name='faq'),
    path('contact_us', views.contact_us_view, name='contact')

]
