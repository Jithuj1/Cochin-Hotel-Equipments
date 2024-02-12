from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from invoice.models.invoice import Invoice
from django.db.models import Q
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re
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
    primary_address = address[0]

    if request.method == 'GET':
        product = Product.objects.all().order_by('-created_at')
    else:
        search = request.POST.get('search')
        q_object = Q()
        # q_object.add(Q(first_name__icontains=search), Q.OR)
        # q_object.add(Q(last_name__icontains=search), Q.OR)
        # q_object.add(Q(phone__icontains=search), Q.OR)

        product = Product.objects.filter(q_object).order_by('-created_at')
    
    page = request.GET.get('page', 1)

    paginator = Paginator(product, 2)
    try:
        product = paginator.page(page)
    except PageNotAnInteger:
        product = paginator.page(1)
    except EmptyPage:
        product = paginator.page(paginator.num_pages)

    context = {
        "product": product, 
        "active_page":"quotation",
        "customer":customer,
        "address":address,
        "primary_address":primary_address
        }
    return render(request, 'quotation/generate_quotation.html', context)