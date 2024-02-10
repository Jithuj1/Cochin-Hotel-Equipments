from django.contrib import admin
from django.urls import path
from home.views.home import home_page

urlpatterns = [
    path('', home_page, name='home'),
]
