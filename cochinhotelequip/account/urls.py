from django.urls import path
from account.views.login import *

urlpatterns = [
    path('login', login_page, name='login'),
    path('logout', logout_view, name='logout'),
]
