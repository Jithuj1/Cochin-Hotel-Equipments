from django.urls import path
from product.views.product import  *
from product.views.category import *

urlpatterns = [
    path('', product, name='product'),
    path('add_product', add_product, name='new_product'),
    path('delete_product/<int:product_id>', delete_product, name='delete_product'),
    path('category', category, name='category'),
    path('add_category', add_category, name='new_category'),
    path('update_product/<int:product_id>', update_product, name='update_product'),
]
