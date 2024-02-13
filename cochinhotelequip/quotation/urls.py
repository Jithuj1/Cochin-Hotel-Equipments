from django.urls import path
from quotation.views.quotation import *


urlpatterns = [
    path('', quotation, name='quotation'),
    path('select_customer', select_customer, name='select_customer'),
    path('generate_quotation/<int:customer_id>', generate_quotation, name='generate_quotation'),
    path('add_invoice_item/<int:invoice_id>/<int:customer_id>', add_invoice_item, name='add_invoice_item'),
    path('delete_quotation_product/<int:item_id>', delete_quotation_product, name='delete_quotation_product'),

]
