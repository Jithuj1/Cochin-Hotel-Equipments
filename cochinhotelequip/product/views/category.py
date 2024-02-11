from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from product.models.product import Product, ItemTax, Category, UnitTypes
from django.db.models import Q
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import re


@login_required(login_url='login')
def category(request):
    if request.method == 'GET':
        category_list = Category.objects.all()

    else:
        search = request.POST.get('search')
        q_object = Q()
        q_object.add(Q(name__icontains=search), Q.OR)

        category_list = Category.objects.filter(q_object)
    
    page = request.GET.get('page', 1)

    paginator = Paginator(category_list, 2)
    try:
        category_list = paginator.page(page)
    except PageNotAnInteger:
        category_list = paginator.page(1)
    except EmptyPage:
        category_list = paginator.page(paginator.num_pages)

    context = {"category_list":category_list, "active_page":"category"}
    return render(request, 'product/category.html', context)
    

@login_required(login_url='login')
def add_category(request):
    if request.method == "POST":
        category = request.POST.get('category')
        if category == "":
            messages.error(request, "category name can't be blank")
            return redirect('category')
        existing_category = Category.objects.filter(name=category).first()
        if existing_category:
            messages.error(request, "category name already exist")
            return redirect('category')
        
        Category.objects.create(name=category)
        return redirect('category')
        

@login_required(login_url='login')
def delete_category(request, category_id):
    Category.objects.get(id=category_id).delete()
    return redirect('category')


@login_required(login_url='login')
def update_category(request, category_id):
    name = request.POST.get('category')
    print(name)
    category = Category.objects.get(id=category_id)
    category.name = name
    category.save()

    return redirect('category')
