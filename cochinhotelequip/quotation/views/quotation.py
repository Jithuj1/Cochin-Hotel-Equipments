from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from invoice.models.invoice import Invoice, InvoiceItem, StoreNames
from django.db.models import Q
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re
from account.models.user import User
from account.models.address import Address
from product.models.product import Product
import datetime
from django.urls import reverse


@login_required(login_url='login')
def quotation(request):
    if request.method == 'GET':
        quotation_list = Invoice.objects.filter(is_quotation=True).order_by('-created_at')
    else:
        search = request.POST.get('search')
        q_object = Q(is_quotation=True)
        q_object.add(Q(customer__first_name__icontains=search), Q.OR)
        q_object.add(Q(customer__last_name__icontains=search), Q.OR)
        q_object.add(Q(quotation_date__icontains=search), Q.OR)
        q_object.add(Q(grand_total__icontains=search), Q.OR)

        quotation_list = Invoice.objects.filter(q_object).order_by('-created_at')

    page = request.GET.get('page', 1)

    paginator = Paginator(quotation_list, 15)
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
    store_names = [ store.value for store in StoreNames]
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

    context = {
        "customers": customers, 
        "active_page":"quotation",
        "store_names" : store_names
        }
    return render(request, 'quotation/select_customer.html', context)


@login_required(login_url='login')
def generate_quotation(request, customer_id):
    customer = User.objects.get(id=customer_id)
    address = Address.objects.filter(customer=customer).order_by('is_default')
    primary_address = address.first()
    if request.method == 'POST':
        store = request.POST.get('store')

        products = Product.objects.all().order_by('-created_at')
        quotation = Invoice.objects.create(customer=customer, address=primary_address, store = store)
    
        return redirect('add_quotation_item', quotation.id, customer.id)

    context = {
        "products": products, 
        "active_page": "quotation",
        "customer": customer,
        "address": address,
        "primary_address": primary_address,
        }

    return render(request, 'quotation/generate_quotation.html', context)


@login_required(login_url='login')
def delete_quotation_product(request, quotation_item_id):
    quotation_item = InvoiceItem.objects.get(id=quotation_item_id)
    quotation_id = quotation_item.invoice.id
    customer_id = quotation_item.invoice.customer.id
    invoice = quotation_item.invoice

    quotation_item.delete()
    invoice.calculate_total()

    return redirect('add_quotation_item', quotation_id, customer_id)
    

@login_required(login_url='login')
def add_quotation_item(request, quotation_id, customer_id):
    customer = User.objects.get(id=customer_id)
    address = Address.objects.filter(customer=customer).order_by('-is_default')
    primary_address = address.first()
    products = Product.objects.all().order_by('-created_at')
    quotation_products = InvoiceItem.objects.filter(invoice=quotation_id).order_by('-created_at')
    quotation = Invoice.objects.get(id=quotation_id)

    if request.method == 'POST':
    
        unit = request.POST.get('unit')
        if not unit:
            messages.error(request, 'Please choose a product.')
            return redirect('add_quotation_item', quotation_id, customer_id)
        product = Product.objects.get(id=unit)
        existing_quotation_item = InvoiceItem.objects.filter(invoice=quotation_id, product=product)
        
        if existing_quotation_item:
            quotation_item = existing_quotation_item.first()
            quotation_item.qty +=1 
        else:
            quotation_item = InvoiceItem(
                product=product, 
                invoice=quotation,
                rate = product.price,
                qty = 1
                )
        quotation_item.save()

        quotation_item.calculate_item_totals()
        quotation_item.invoice.calculate_total()
        return redirect('add_quotation_item', quotation_id, customer_id)
 

    quotation = Invoice.objects.get(id=quotation_id)

    context = {
        "products": products, 
        "active_page": "quotation",
        "customer": customer,
        "address_list": address,
        "primary_address": primary_address,
        'quotation': quotation,
        "quotation_products": quotation_products if quotation_products else None,
        'invoice_id': quotation_id,
        }
    return render(request, 'quotation/generate_quotation.html', context)


def edit_quotation_item(request, quotation_item_id, quotation_id, customer_id):
    if request.method == 'POST':

        quantity = int(request.POST.get('quantity'))
        rate = float(request.POST.get('rate'))

        quotation_item = InvoiceItem.objects.get(id=quotation_item_id)
        quotation_item.qty = quantity
        quotation_item.rate = rate
        quotation_item.save()
        
        quotation_item.calculate_item_totals()
        quotation_item.invoice.calculate_total()

        return redirect('add_quotation_item', quotation_id, customer_id)
    

@login_required(login_url='login')
def delete_quotation(request, quotation_id):
    InvoiceItem.objects.filter(invoice =quotation_id).delete()
    Invoice.objects.get(id=quotation_id).delete()
    return redirect('quotation')


@login_required(login_url='login')
def save_quotation(request, quotation_id):
    quotation = Invoice.objects.get(id=quotation_id)
    quotation_items = InvoiceItem.objects.filter(invoice=quotation)
    if len(quotation_items) == 0:
        quotation.delete()
        return redirect('quotation')
    quotation_items.update(is_active=True)
    quotation.generate_quotaion_num()
    quotation.calculate_total()
    return redirect('quotation')


@login_required(login_url='login')
def change_delivery_address(request, quotation_id, customer_id, address_id):
    Address.objects.filter(customer=customer_id).update(is_default=False)
    address =Address.objects.get(id=address_id)
    address.is_default = True
    address.save()
    return redirect('add_quotation_item', quotation_id, customer_id)


@login_required(login_url='login')
def add_discount(request, quotation_id, customer_id):
    if request.method == 'POST':

        discount = request.POST.get('discount')
        discount = int(discount.split(".")[0])

        quotation = Invoice.objects.get(id=quotation_id)
        if discount > quotation.amount_remaining:
            messages.error(request, "You can't provide discount more than amount remaining")
            return redirect('add_quotation_item', quotation_id, customer_id)
        quotation.discount = discount
        quotation.save()
        
        quotation.calculate_total()

        return redirect('add_quotation_item', quotation_id, customer_id)
    

@login_required(login_url='login')
def make_payment(request, quotation_id):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        amount = amount.split(".")[0]
        page_number = int(request.POST.get('page_value'))

        quotation = Invoice.objects.get(id=quotation_id)

        response = quotation.make_payment(int(amount))

        if not response["status"] :
            messages.error(request, response["message"])
            return redirect(reverse('quotation')+f'?page={page_number}')
        
        return redirect(reverse('quotation')+f'?page={page_number}')


@login_required(login_url='login')
def convert_to_invoice(request, quotation_id: int):
    quotation = Invoice.objects.get(id=quotation_id)
    quotation_items = InvoiceItem.objects.filter(invoice=quotation_id)
    if len(quotation_items) == 0:
        quotation.delete()
        return redirect('quotation')
    
    quotation.is_quotation = False
    quotation.invoice_date = datetime.date.today()
    quotation.save()

    quotation_items.update(is_active = True)
    quotation.generate_invoice_num()
    return redirect('invoice')