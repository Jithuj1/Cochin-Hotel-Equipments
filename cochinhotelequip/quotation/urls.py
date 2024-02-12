from django.urls import path
from quotation.views.quotation import *


urlpatterns = [
    path('', quotation, name='quotation'),
    path('select_customer', select_customer, name='select_customer'),
    path('generate_quotation/<int:customer_id>', generate_quotation, name='generate_quotation'),
]
