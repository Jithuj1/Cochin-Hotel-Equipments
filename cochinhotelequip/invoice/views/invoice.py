from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from invoice.models.invoice import Invoice, InvoiceItem, StoreNames
from django.db.models import Q
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required(login_url='login')
def invoice(request):
    invoice = Invoice.objects.filter(is_quotation=True).order_by('-invoice_date')
    context = {
        'invoice': invoice,
        "active_page": "invoice",

    }
    return render(request, 'invoice/invoice.html', context)


@login_required(login_url='login')
def convert_to_invoice(request, invoice_id: int):
    invoice = Invoice.objects.get(id=invoice_id)
    invoice_items = InvoiceItem.objects.filter(invoice=invoice)
    if len(invoice_items) == 0:
        invoice.delete()
        return redirect('invoice')
    invoice.generate_quotaion_num()
    invoice.calculate_total()
    invoice.is_quotation = True
    invoice.save()
    return redirect('invoice')