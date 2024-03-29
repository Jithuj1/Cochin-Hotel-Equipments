from django.urls import path
from invoice.views.invoice import *


urlpatterns = [
    path('', invoice, name='invoice'),
    path('<int:invoice_id>', view_invoice, name='view_invoice'),
    path('add_discount/<int:invoice_id>', add_discount, name='add_discount'),
    path('delete_invoice/<int:invoice_id>', delete_invoice, name='delete_invoice'),
    path('invoice_make_payment/<int:invoice_id>', make_payment, name='invoice_make_payment'),
    path('edit_invoice_item/<int:invoice_id>/<int:invoice_item_id>', 
         edit_invoice_item, name='edit_invoice_item'),
    path('delete_invoice_product/<int:invoice_id>/<int:invoice_item_id>', 
         delete_invoice_product, name='delete_invoice_product'),
]
