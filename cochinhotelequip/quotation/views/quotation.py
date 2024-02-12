from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from invoice.models.invoice import Invoice
from django.db.models import Q
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re


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
    