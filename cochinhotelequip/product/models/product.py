from django.db import models
from enum import Enum
from django.utils.translation import gettext_lazy as _

from cochinhotelequip.utils.base_model import BaseModel

class UnitTypes(Enum):
        PIECE = "PIECE"

class Category(BaseModel):
    name = models.CharField(max_length=128, null=False, blank=-False)


class Product(BaseModel):

    name = models.CharField(max_length=128, blank=False)
    category = models.ForeignKey("product.Category", verbose_name=_("product_category"), on_delete=models.CASCADE)
    unit = models.CharField(choices=[(options.name, options.value) for options in UnitTypes], max_length=20)
    hsn_code = models.CharField(max_length=25, blank=False)
    is_active = models.BooleanField(default=True)
    is_taxable = models.BooleanField(default=True)
    tax_perc = models.FloatField(default=18)
    remark = models.TextField(blank=True)



class ItemTax(BaseModel):
    product = models.ForeignKey("product.Product", verbose_name=_("product_tax"), on_delete=models.CASCADE)
    igst = models.FloatField(null=True)
    sgst = models.FloatField(null=True)
    cgst = models.FloatField(null=True)