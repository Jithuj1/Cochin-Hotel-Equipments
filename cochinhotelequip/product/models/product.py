from django.db import models
from enum import Enum
from django.utils.translation import gettext_lazy as _

from cochinhotelequip.utils.base_model import BaseModel

class UnitTypes(Enum):
        PIECE = "PIECE"
        SET = "SET"
        NUMBER = "NUMBER"
        OTHERS = "OTHERS"

class Category(BaseModel):
    name = models.CharField(max_length=128, null=False, blank=-False)


class Product(BaseModel):

    name = models.CharField(max_length=128, blank=False)
    category = models.ForeignKey("product.Category", on_delete=models.PROTECT)
    unit = models.CharField(choices=[(options.name, options.value) for options in UnitTypes], max_length=20)
    hsn_code = models.CharField(max_length=25, blank=False)
    price = models.FloatField(null=False, default = 0)
    is_active = models.BooleanField(default=True)
    is_taxable = models.BooleanField(default=True)
    tax_perc = models.FloatField(default=18)
    remark = models.TextField(blank=True)
