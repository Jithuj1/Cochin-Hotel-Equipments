from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from invoice.models.invoice import Invoice, InvoiceItem, StoreNames
from account.models.user import User
from account.models.address import Address
from django.http import HttpResponse
import pdfkit
from django.template.loader import get_template
import tempfile


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
    context = {
        "quotation": quotation,
        "customer_address": customer_address,
        "quotation_items":quotation_items,
        "customer": customer_address.customer,
        "total_gst": quotation.tax_igst_total + quotation.tax_cgst_total + quotation.tax_sgst_total,
        "company_address": company_address_ernakulam if quotation.store == "ERNAKULAM" else company_address_thissur
    }

    header_context = {
        "quotation": quotation,
        "date":quotation.quotation_date if quotation.is_quotation else quotation.invoice_date
    }
    footer_context = {
        "store": True if quotation.store == "ERNAKULAM" else False
    }

    body_html = get_template('printable/quotation.html')
    footer_template = get_template('printable/footer.html')
    header_template = get_template('printable/header.html')
    footer_file =  footer_template.render(footer_context)
    header_file =  header_template.render(header_context)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as footer_html_file:
        footer_html_file.write(footer_file.encode("utf-8"))
        footer_file_path = footer_html_file.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as header_html_file:
        header_html_file.write(header_file.encode("utf-8"))
        header_file_path = header_html_file.name

    html = body_html.render(context)

    pdf_options = {
        "page-size": "A4",
        "margin-top": "1.85in",
        "margin-right": "0.25in",
        "margin-bottom": "0.75in",
        "margin-left": "0.25in",
        "encoding": "UTF-8",
        "disable-smart-shrinking": None,
        "enable-local-file-access": None,
        "--keep-relative-links": "",
        "dpi": 500,
        "footer-html": footer_file_path,
        "header-html": header_file_path,
    }

    pdf_file = pdfkit.from_string(
        html,
        verbose=True,
        options=pdf_options
    )

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=quotation.pdf'

    return response
