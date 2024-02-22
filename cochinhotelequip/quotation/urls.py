from django.urls import path
from quotation.views.quotation import *
from quotation.views.printable import * 


urlpatterns = [
    path('', quotation, name='quotation'),
    path('select_customer', select_customer, name='select_customer'),
    path('generate_quotation/<int:customer_id>', generate_quotation, name='generate_quotation'),
    path('add_quotation_item/<int:quotation_id>/<int:customer_id>', add_quotation_item, name='add_quotation_item'),
    path('edit_quotation_item/<int:quotation_item_id>/<int:quotation_id>/<int:customer_id>', edit_quotation_item, name='edit_quotation_item'),
    path('delete_quotation_product/<int:quotation_item_id>', delete_quotation_product, name='delete_quotation_product'),
    path('delete_quotation/<int:quotation_id>', delete_quotation, name='delete_quotation'),
    path('save_quotation/<int:quotation_id>', save_quotation, name='save_quotation'),
    path('change_delivery_address/<int:quotation_id>/<int:customer_id>/<int:address_id>', change_delivery_address, name='change_delivery_address'),
    path('generate_quotation_pdf/<int:quotation_id>', generate_quotation_pdf, name='generate_quotation_pdf'),
    path('add_discount/<int:quotation_id>/<int:customer_id>', add_discount, name="add_discount"),
    path('make_payment/<int:quotation_id>', make_payment, name="make_payment"),
    path('convert-to-invoice/<int:quotation_id>', convert_to_invoice, name='convert_to_invoice'),
]
