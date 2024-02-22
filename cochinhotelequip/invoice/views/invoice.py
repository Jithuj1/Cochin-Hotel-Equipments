from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from invoice.models.invoice import Invoice, InvoiceItem, StoreNames
from django.db.models import Q
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required(login_url='login')
def invoice(request):
    invoice_list = Invoice.objects.filter(is_quotation=False).order_by('-invoice_date')
    context = {
        'invoice_list': invoice_list,
        "active_page": "invoice",

    }
    return render(request, 'invoice/invoice.html', context)
