from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from invoice.models.invoice import Invoice, InvoiceItem
from django.db.models import Q
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re
from django.shortcuts import get_object_or_404
from account.models.user import User
from account.models.address import Address
from product.models.product import Product


@login_required(login_url='login')
def quotation(request):
    if request.method == 'GET':
        quotation_list = Invoice.objects.filter(is_quotation=True).order_by('-created_by')
        
    else:
        search = request.POST.get('search')
        q_object = Q()
        q_object.add(Q(customer__first_name__icontains=search), Q.OR)
        q_object.add(Q(customer__last_name__icontains=search), Q.OR)
        q_object.add(Q(quotation_date__icontains=search), Q.OR)
        q_object.add(Q(grand_total__icontains=search), Q.OR)

        quotation_list = Invoice.objects.filter(q_object).order_by('-created_by')

    page = request.GET.get('page', 1)

    paginator = Paginator(quotation_list, 2)
    try:
        quotation_list = paginator.page(page)
    except PageNotAnInteger:
        quotation_list = paginator.page(1)
    except EmptyPage:
        quotation_list = paginator.page(paginator.num_pages)

    context = {"quotation_list":quotation_list, "active_page":"quotation"}
    return render(request, 'quotation/quotation.html', context)


@login_required(login_url='login')
def select_customer(request):
    if request.method == 'GET':
        customers = User.objects.all().order_by("-date_joined")
    else:
        search = request.POST.get('search')
        q_object = Q()
        q_object.add(Q(first_name__icontains=search), Q.OR)
        q_object.add(Q(last_name__icontains=search), Q.OR)
        q_object.add(Q(phone__icontains=search), Q.OR)

        customers = User.objects.filter(q_object).order_by("-date_joined")
    
    page = request.GET.get('page', 1)

    paginator = Paginator(customers, 2)
    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)

    context = {"customers": customers, "active_page":"quotation"}
    return render(request, 'quotation/select_customer.html', context)


@login_required(login_url='login')
def generate_quotation(request, customer_id):
    customer = User.objects.get(id=customer_id)
    address = Address.objects.filter(customer=customer).order_by('is_default')
    primary_address = address.first()
    if request.method == 'GET':
        products = Product.objects.all().order_by('-created_at')
        invoice = Invoice.objects.create(customer=customer,discount=9.0,amount_paid=0,amount_remaining=0,grand_total=0)
    
       

    
        # products = Product.objects.filter(q_object).order_by('-created_at')
        return redirect('add_invoice_item', invoice.id, customer.id)
        # quotation_products = InvoiceItem.objects.filter(invoice=invoice).order_by('-created_at')
        # q_object.add(Q(first_name__icontains=search), Q.OR)
        # q_object.add(Q(last_name__icontains=search), Q.OR)
        # q_object.add(Q(phone__icontains=search), Q.OR)

    page = request.GET.get('page', 1)

        # paginator = Paginator(products, 3)
        # try:
        #     products = paginator.page(page)
        # except PageNotAnInteger:
        #     products = paginator.page(1)
        # except EmptyPage:
        #     products = paginator.page(paginator.num_pages)

    context = {
        "products": products, 
        "active_page": "quotation",
        "customer": customer,
        "address": address,
        "primary_address": primary_address,
        # "quotation_products": quotation_products if quotation_products else None,
        }
    print(primary_address.city)
    return render(request, 'quotation/generate_quotation.html', context)

@login_required(login_url='login')
def delete_quotation_product(request, item_id):
    invoice_item = InvoiceItem.objects.get(id=item_id)
    invoice_id = invoice_item.invoice.id
    customer_id = invoice_item.invoice.customer.id
    invoice_item.delete()
    return redirect('add_invoice_item', invoice_id, customer_id)
    
@login_required(login_url='login')
def add_invoice_item(request, invoice_id, customer_id):
    customer = User.objects.get(id=customer_id)
    address = Address.objects.filter(customer=customer).order_by('is_default')
    primary_address = address.first()
    products = Product.objects.all().order_by('-created_at')
    quotation_products = InvoiceItem.objects.filter(invoice=invoice_id).order_by('-created_at')
    if request.method == 'POST':
    
        unit = request.POST.get('unit')
        if not unit:
            messages.error(request, 'Please choose a product.')
            return redirect('add_invoice_item', invoice_id, customer_id)
            
        invoice = get_object_or_404(Invoice, pk=invoice_id)
        invoice_item = InvoiceItem(product=Product.objects.get(id=unit), invoice=invoice)
        invoice_item.save()
    context = {
        "products": products, 
        "active_page": "quotation",
        "customer": customer,
        "address": address,
        "primary_address": primary_address,
        "quotation_products": quotation_products if quotation_products else None,
        }
    return render(request, 'quotation/generate_quotation.html', context)
