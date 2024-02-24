from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from invoice.models.invoice import Invoice, InvoiceItem, StoreNames
from django.db.models import Q
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required(login_url='login')
def invoice(request):
    if request.method == 'GET':
        invoice_list = Invoice.objects.filter(is_quotation=False).order_by('-created_at')
    else:
        search = request.POST.get('search')
        q_object = Q(is_quotation=False)
        q_object.add(Q(customer__first_name__icontains=search), Q.OR)
        q_object.add(Q(customer__last_name__icontains=search), Q.OR)
        q_object.add(Q(quotation_date__icontains=search), Q.OR)
        q_object.add(Q(grand_total__icontains=search), Q.OR)

        invoice_list = Invoice.objects.filter(q_object).order_by('-created_at')

    page = request.GET.get('page', 1)

    paginator = Paginator(invoice_list, 2)
    try:
        invoice_list = paginator.page(page)
    except PageNotAnInteger:
        invoice_list = paginator.page(1)
    except EmptyPage:
        invoice_list = paginator.page(paginator.num_pages)

    context = {"invoice_list":invoice_list, "active_page":"invoice"}
    return render(request, 'invoice/invoice.html', context)
   
   
@login_required(login_url='login')
def view_invoice(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    invoice_items = InvoiceItem.objects.filter(invoice=invoice)
    page_number = request.GET.get('page')
    context = {
        "invoice": invoice,
        "invoice_items": invoice_items,
        "address":invoice.address,
        "active_page":"invoice",
        "page":page_number,
    }

    return render(request, 'invoice/invoice_detail.html', context)


@login_required(login_url='login')
def add_discount(request, invoice_id):
    if request.method == 'POST':

        discount = request.POST.get('discount')

        invoice = Invoice.objects.get(id=invoice_id)
        if int(discount) > invoice.amount_remaining:
            messages.error(request, "You can't provide discount more than amount remaining")
            return redirect('view_invoice', invoice)
        invoice.discount = discount
        invoice.save()
        
        invoice.calculate_total()

        return redirect('view_invoice', invoice_id)
    

@login_required(login_url='login')
def make_payment(request, invoice_id):
    if request.method == 'POST':
        amount = int(request.POST.get('amount'))
        page_number = request.GET.get('page')

        invoice = Invoice.objects.get(id=invoice_id)

        response = invoice.make_payment(amount)

        if not response["status"] :
            messages.warning(request, response["message"])
            return redirect(reverse('invoice')+f'?page={page_number}')
        
        return redirect(reverse('invoice')+f'?page={page_number}')