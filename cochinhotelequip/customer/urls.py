from django.urls import path
from customer.views.customer import *

urlpatterns = [
    path('', customer, name='customer'),
    path('add_customer', add_customer, name='new_customer'),
    path('delete_customer/<int:customer_id>', delete_customer, name='delete_customer'),
    path('view_customer/<int:customer_id>', view_customer, name='view_customer'),
    path('add_address/<int:customer_id>', add_address, name='add_address'),
    path('update_customer/<int:customer_id>', update_customer, name='update_customer'),
    path('update_address/<int:address_id>', update_address, name='update_address'),
]
