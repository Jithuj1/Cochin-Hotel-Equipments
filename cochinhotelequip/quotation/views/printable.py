from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from invoice.models.invoice import Invoice, InvoiceItem, StoreNames
from account.models.user import User
from account.models.address import Address
from django.http import HttpResponse
import pdfkit
from django.template.loader import get_template


@login_required(login_url='login')
def generate_quotation_pdf(request, quotation_id):
    quotation = Invoice.objects.get(id=quotation_id)
    customer_address = Address.objects.get(id=quotation.address.id)
    quotation_items = InvoiceItem.objects.filter(invoice = quotation).order_by('created_at')
    company_address_thissur = {
        "street1": "Peramangalam",
        "street2":"BLD #144 Near AMALA HOSPITAL",
        "city":"Kunnamkulam Rd, Thirssur",
        "state":"Kerala",
        "zipcode":"680503",
        "phone":"+91 7034222220"
    }
    company_address_ernakulam = {
        "street1": "Muttam, Choornikara",
        "street2":"Kalamasserty, CMS College Rd, Ernakulam",
        "city":"Ernakulam",
        "state":"Kerala",
        "zipcode":"680503",
        "phone":"+91 7034222220"
    }
    
    bank_details_thirssur = {
        "account_holder": "Vineesh Thomas",
        "acc_no":"626405021352",
        "bank_name":"ICICI Bank Ltd",
        "branch":"EDAPALLYERNAKULAM",
        "ifsc":"ICIC0006264"
    }

    bank_details_ernakulam = {
        "account_holder": "COCHIN HOTEL EQUIPMENTS",
        "acc_no":"10120200026759",
        "bank_name":"FEDERALBANK",
        "branch":"KALAMASSERY Br.[Kl]",
        "ifsc":"FDRL0001012"
    }

    context = {
        "is_quotation":quotation.is_quotation,
        "quotation": quotation,
        "customer_address": customer_address,
        "quotation_items":quotation_items,
        "customer": customer_address.customer,
        "total_gst": quotation.tax_igst_total + quotation.tax_cgst_total + quotation.tax_sgst_total,
        "company_address": company_address_ernakulam if quotation.store == "ERNAKULAM" else company_address_thissur,
        "bank_details": bank_details_ernakulam if quotation.store == "ERNAKULAM" else bank_details_thirssur
    }

    body_html = get_template('printable/quotation.html')

    html = body_html.render(context)

    pdf_options = {
        "page-size": "A4",
        "margin-top": "0.25in",
        "margin-right": "0.25in",
        "margin-bottom": "0.25in",
        "margin-left": "0.25in",
        "encoding": "UTF-8",
        "dpi": 500,
    }

    pdf_file = pdfkit.from_string(
        html,
        verbose=True,
        options=pdf_options
    )

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=quotation.pdf'

    return response
