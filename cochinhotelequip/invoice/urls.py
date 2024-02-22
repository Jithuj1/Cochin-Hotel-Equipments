from django.urls import path
from invoice.views.invoice import *


urlpatterns = [
    path('', invoice, name='invoice'),
    path('convert-to-invoice/<int:invoice_id>', convert_to_invoice, name='convert_to_invoice'),

]
