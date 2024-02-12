from django.urls import path
from quotation.views.quotation import *


urlpatterns = [
    path('', quotation, name='quotation'),
    # path('delete_product/<int:product_id>', delete_product, name='delete_product'),
]
