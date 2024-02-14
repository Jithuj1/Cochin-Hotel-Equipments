from django.db import models
from enum import Enum
from django.utils.translation import gettext_lazy as _
from django.db import IntegrityError
from cochinhotelequip.utils.base_model import BaseModel
from account.models.address import Address
from invoice.utils.gst_calculater import calculate_gst
from invoice.utils.financial_year import fiscal_year_4digit

class Invoice(BaseModel):

    quotation_date = models.DateField(auto_now_add=True)
    invoice_date = models.DateField(null=True)
    customer = models.ForeignKey("account.User", on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    is_quotation = models.BooleanField(default=True)
    discount = models.FloatField(default=0)
    amount_paid = models.FloatField()
    amount_remaining = models.FloatField()
    grand_total = models.FloatField()
    tax_igst_total = models.FloatField(default=0)
    tax_sgst_total = models.FloatField(default=0)
    tax_cgst_total = models.FloatField(default=0)
    invoice_num_seq = models.IntegerField(null=True)
    invoice_num_fiscalyr = models.IntegerField(null=True)

    class Meta(BaseModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["invoice_num_seq", "invoice_num_fiscalyr"],
                name="unique_fiscalyr_seq_num",
            )
        ]

    def generate_invoice_num(self):
        fiscal_year_code = fiscal_year_4digit()

        highest_invoice_num_obj = (
            Invoice.objects.filter(invoice_num_fiscalyr=fiscal_year_code)
            .order_by("-invoice_num_seq")
            .first()
        )

        current_invoice_num = (
            highest_invoice_num_obj.invoice_num_seq if highest_invoice_num_obj else 1
        )

        self.invoice_num_fiscalyr = fiscal_year_code
        new_invoice_num_seq = current_invoice_num

        while True:
            self.invoice_num_seq = new_invoice_num_seq
            try:
                self.save()
                break
            except IntegrityError:
                new_invoice_num_seq += 1

    def calculate_total(self):
        tax_igst_total = tax_sgst_total = tax_cgst_total = sub_total = 0

        child_invoice_items = InvoiceItem.objects.filter(invoice=self)
        for item in child_invoice_items:
            tax_igst, tax_sgst, tax_cgst = item.igst, item.sgst, item.cgst

            tax_igst_total += tax_igst
            tax_sgst_total += tax_sgst
            tax_cgst_total += tax_cgst

            sub_total += item.sub_total

        grand_total = sub_total + tax_igst_total + tax_sgst_total + tax_cgst_total - self.discount

        self.tax_igst_total = round(tax_igst_total, 2)
        self.tax_sgst_total = round(tax_sgst_total, 2)
        self.tax_cgst_total = round(tax_cgst_total, 2)
        self.sub_total = round(sub_total, 2)
        self.grand_total = round(grand_total, 2)
        self.save()


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


    def calculate_item_totals(self, billing_state, billing_country):
        igst, sgst, cgst = calculate_gst(
            self.rate, 
            self.product.tax_perc, 
            billing_state, 
            billing_country
            )
        
        self.igst = igst
        self.sgst = sgst
        self.cgst = cgst
        self.total_gst = igst + sgst + cgst
        self.sub_total = self.rate * self.qty
        self.grand_item_total = self.total_gst + (self.rate * self.qty)
        self.save()






