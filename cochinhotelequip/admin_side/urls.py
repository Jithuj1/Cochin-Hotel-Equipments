from django.urls import path
from admin_side.views.admin_home import *

urlpatterns = [
    path('', admin_home_page, name='admin_home'),
]
