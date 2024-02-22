from django.db import models
from enum import Enum
from django.utils.translation import gettext_lazy as _
from django.db import IntegrityError
from cochinhotelequip.utils.base_model import BaseModel
from account.models.address import Address
from invoice.utils.gst_calculater import calculate_gst
from invoice.utils.financial_year import fiscal_year_4digit


class StoreNames(Enum):
        ERNAKULAM = "ERNAKULAM"
        THRISSUR = "THRISSUR"


class Invoice(BaseModel):

    quotation_date = models.DateField(auto_now_add=True)
    invoice_date = models.DateField(null=True)
    customer = models.ForeignKey("account.User", on_delete=models.PROTECT)
    address = models.ForeignKey("account.Address", on_delete=models.PROTECT)
    store = models.CharField(choices=[(options.name, options.value) for options in StoreNames], max_length=20)
    is_active = models.BooleanField(default=True)
    is_quotation = models.BooleanField(default=True)
    discount = models.FloatField(default=0)
    amount_paid = models.IntegerField(default=0)
    amount_remaining = models.IntegerField(default=0)
    sub_total = models.FloatField(default=0)
    grand_total = models.FloatField(default=0)
    tax_igst_total = models.FloatField(default=0)
    tax_sgst_total = models.FloatField(default=0)
    tax_cgst_total = models.FloatField(default=0)
    invoice_num_seq = models.IntegerField(null=True)
    quotation_num_seq = models.IntegerField(null=True)
    invoice_num_fiscalyr = models.IntegerField(null=True)

    class Meta(BaseModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["invoice_num_seq", "invoice_num_fiscalyr"],
                name="invoice_unique_fiscalyr_seq_num",
            ),
            models.UniqueConstraint(
                fields=["quotation_num_seq", "invoice_num_fiscalyr"],
                name="quotation_unique_fiscalyr_seq_num",
            )
        ]

    def generate_quotaion_num(self):
        fiscal_year_code = fiscal_year_4digit()

        highest_quotation_num_obj = (
            Invoice.objects.filter(invoice_num_fiscalyr=fiscal_year_code, is_quotation=True)
            .order_by("-invoice_num_seq")
            .first()
        )

        self.invoice_num_fiscalyr = fiscal_year_code

        current_quotaion_num = (
            highest_quotation_num_obj.quotation_num_seq if highest_quotation_num_obj else 1
        )

        new_quotaion_num_seq = current_quotaion_num

        while True:
            self.quotation_num_seq = new_quotaion_num_seq
            try:
                self.save()
                break
            except IntegrityError:
                new_quotaion_num_seq += 1

    def generate_invoice_num(self):
        fiscal_year_code = fiscal_year_4digit()

        highest_invoice_num_obj = (
            Invoice.objects.filter(invoice_num_fiscalyr=fiscal_year_code, is_quotation=False)
            .order_by("-invoice_num_seq")
            .first()
        )

        current_invoice_num = (
            highest_invoice_num_obj.invoice_num_seq if highest_invoice_num_obj else 1
        )

        new_invoice_num_seq = current_invoice_num

        while True:
            self.invoice_num_seq = new_invoice_num_seq
            try:
                self.save()
                break
            except IntegrityError:
                new_invoice_num_seq += 1

    def calculate_total(self):
        child_invoice_items = InvoiceItem.objects.filter(invoice=self)

        sub_total = sum([item.sub_total for item in child_invoice_items])
        grand_total = sub_total - self.discount

        self.sub_total = round(sub_total, 2)
        self.grand_total = round(grand_total)
        self.amount_remaining = grand_total - self.amount_paid
        self.save()

    def make_payment(self, amount):
        if self.amount_remaining < amount:
            response = {
                "status": False,
                "message":"Paying amount greater than remaining amount"
            }
            return response
        
        self.amount_paid = self.amount_paid + amount
        self.amount_remaining = self.grand_total - self.amount_paid
        self.save()
        response = {
                "status": True,
                "message":"Paid"
            }
        return response


    @property
    def invoice_num(self):
        if not self.is_quotation:
            invoice_num_seq_in_five_digit = str(self.invoice_num_seq).zfill(5)
            return (
                f"CHE/IVC/{self.invoice_num_fiscalyr}/{invoice_num_seq_in_five_digit}"
            )
        else:
            quotation_num_seq_in_five_digit = str(self.quotation_num_seq).zfill(5)
            return (
                f"CHE/QTN/{self.invoice_num_fiscalyr}/{quotation_num_seq_in_five_digit}"
            )


class InvoiceItem(BaseModel):
    invoice = models.ForeignKey("invoice.Invoice", on_delete=models.CASCADE)
    product = models.ForeignKey("product.Product", on_delete=models.PROTECT)
    igst = models.FloatField(null=True)
    sgst = models.FloatField(null=True)
    cgst = models.FloatField(null=True)
    total_gst = models.FloatField(null=True)
    is_active = models.BooleanField(default=False)
    qty = models.IntegerField(default=1)
    rate = models.FloatField(null=False, default=0)  ## TODO : remove default before production
    grand_item_total = models.FloatField(null=True)
    sub_total = models.FloatField(null=True)


    def calculate_item_totals(self):
        self.sub_total = self.rate * self.qty
        self.save()






