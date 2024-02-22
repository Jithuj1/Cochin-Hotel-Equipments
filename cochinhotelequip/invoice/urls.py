from django.urls import path
from invoice.views.invoice import *


urlpatterns = [
    path('', invoice, name='invoice'),
]
