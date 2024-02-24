from django.urls import path
from invoice.views.invoice import *


urlpatterns = [
    path('', invoice, name='invoice'),
    path('<int:invoice_id>', view_invoice, name='view_invoice'),
    path('add_discount/<int:invoice_id>', add_discount, name='add_discount'),
    path('invoice_make_payment/<int:invoice_id>', make_payment, name='invoice_make_payment'),
]
