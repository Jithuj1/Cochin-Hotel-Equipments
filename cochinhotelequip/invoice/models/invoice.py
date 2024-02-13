from django.db import models
from enum import Enum
from django.utils.translation import gettext_lazy as _

from cochinhotelequip.utils.base_model import BaseModel


class Invoice(BaseModel):

    quotation_date = models.DateField(auto_now_add=True)
    invoice_date = models.DateField(null=True)
    customer = models.ForeignKey("account.User", on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    is_quotation = models.BooleanField(default=True)
    discount = models.FloatField()
    amount_paid = models.FloatField()
    amount_remaining = models.FloatField()
    grand_total = models.FloatField()


class InvoiceItem(BaseModel):
    invoice = models.ForeignKey("invoice.Invoice", on_delete=models.CASCADE)
    product = models.ForeignKey("product.Product", on_delete=models.SET_NULL, null=True)
    igst = models.FloatField(null=True)
    sgst = models.FloatField(null=True)
    cgst = models.FloatField(null=True)
    total_gst = models.FloatField(null=True)
    is_active = models.BooleanField(default=False)
