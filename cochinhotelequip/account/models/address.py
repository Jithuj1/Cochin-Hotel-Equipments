from django.db import models
from enum import Enum
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from cochinhotelequip.utils.base_model import BaseModel
from account.models.user import User


class Address(BaseModel):

    class AddressTypes(Enum):
        BILLING = "BILLING"
        DELIVERY = "DELIVERY"
        PERSONAL = "PERSONAL"

    address_type = models.CharField(choices=[(options.name, options.value) for options in AddressTypes], max_length=10)
    customer = models.ForeignKey("account.User", verbose_name=_("customers"), on_delete=models.CASCADE)

    street1 = models.CharField(max_length=128, blank=True)
    street2 = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=128, blank=True)
    state = models.CharField(max_length=128, blank=True)
    country = models.CharField(max_length=128)
    zipcode = models.CharField(max_length=128, blank=True)
    phone = PhoneNumberField(null=True, blank=True)
    is_default = models.BooleanField(default=False)
    lan_mark = models.CharField(max_length=50, null=True)

    def update_customer_details(self):
        if not str(self.phone).startswith("+91"):
            # If not, prepend "+91" to the phone number
            self.phone = "+91" + str(self.phone)

       
        # Save the changes
        self.save()