from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from product.models.product import Product, Category, UnitTypes
from django.db.models import Q
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
import re

from django.http import HttpResponseBadRequest
from django.db.models.deletion import ProtectedError


@login_required(login_url='login')
def product(request):
    if request.method == 'GET':
        products = Product.objects.all().order_by("-created_at")

    else:
        search = request.POST.get('search')
        q_object = Q()
        q_object.add(Q(name__icontains=search), Q.OR)
        q_object.add(Q(category__name__icontains=search), Q.OR)

        products = Product.objects.filter(q_object).order_by("-created_at")
    
    page = request.GET.get('page', 1)

    paginator = Paginator(products, 15)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {"products":products, "active_page":"product"}
    return render(request, 'product/product.html', context)
    

@login_required(login_url='login')
def add_product(request):
    if request.method == 'GET':
        category_list = Category.objects.all().order_by('name')
        units = [unit.value for unit in UnitTypes]
        context = {
            "category_list":category_list,
            "units":units
            }
        return render(request, 'product/add_product.html', context)
    else:
        product_name = request.POST.get('product_name')
        hsn_code = request.POST.get('hsn_code')
        Is_taxable = request.POST.get('Is_taxable')
        tax_perc = request.POST.get('tax_perc')
        unit = request.POST.get('unit')
        price = request.POST.get('price')
        category = request.POST.get('category')
        remarks = request.POST.get('remarks')

        if product_name == "" or hsn_code == "" or tax_perc == "" or category=="":
            messages.error(request, "product_name, hsn_code, category and tax_perc can't be blank")
            return redirect('new_product')
        try:
            int_value = int(tax_perc)
        except ValueError:
            try:
                float_value = float(tax_perc)
                tax_perc = "{:.2f}".format(float_value)
            except ValueError:
                messages.error(request, "please enter a numerical value for tax ")
                return redirect('new_product')
            
        try:
            int_value = int(price)
        except ValueError:
            try:
                float_value = float(price)
                price = "{:.2f}".format(float_value)
            except ValueError:
                messages.error(request, "please enter a numerical value for price ")
                return redirect('new_product')
        
        category_obj = Category.objects.filter(id=category).first()
        if not category_obj:
            messages.error(request, "Category not found")
            return redirect('new_product')
        try:
            product = Product.objects.create(
                name = product_name,
                hsn_code = hsn_code,
                unit = unit,
                price = price,
                category = category_obj,
                tax_perc = tax_perc,
                remark = remarks,
                is_taxable = Is_taxable,
            )

            return redirect('product')
        except Exception as e :
            messages.error(request, f"{e}")
            return redirect('new_product')
    

@login_required(login_url='login')
def delete_product(request, product_id):
    try:
        page_number =  request.GET.get('page')

        Product.objects.get(id=product_id).delete()
    except  ProtectedError:
        messages.warning(request, "Cannot delete this product because it is referenced by other objects.")

    return redirect(reverse('product')+f'?page={page_number}')


@login_required(login_url='login')
def update_product(request, product_id):

   
    page_number =  request.GET.get('page')

    product = Product.objects.filter(id=product_id).first()
    category_list = Category.objects.all()
    if product and product.category:
        category_list = [product.category] + [
            category for category in category_list if category != product.category]
    context = {
        "product":product,
        "category_list":category_list,
        "active_page":"product",
        'page_number': page_number,
        }
    if request.method =="GET":
        
        return  render(request, 'product/update_product.html', context) 
    else:
        page_number =  request.GET.get('page')

        product_name = request.POST.get('product_name')
        hsn_code = request.POST.get('hsn_code')
        tax_perc = request.POST.get('tax_perc')
        category = request.POST.get('category')
        remarks = request.POST.get('remarks')
        price = request.POST.get('price')

        if any(value is not None and value.isspace() 
               for value in [product_name, hsn_code, tax_perc, category, remarks, price]):
            messages.error(request, "Input cannot be blank or None")
            url = reverse('update_product', kwargs={'product_id': product_id})
            return redirect(url)
        
        if tax_perc:
            try:
                int_value = int(tax_perc)
            except ValueError:
                try:
                    float_value = float(tax_perc)
                    tax_perc = "{:.2f}".format(float_value)
                except ValueError:
                    messages.error(request, "please enter a numerical value for tax ")
                    url = reverse('update_product', kwargs={'product_id': product_id})
                    return redirect(url)
                
        if price:
            try:
                int_value = int(price)
            except ValueError:
                try:
                    float_value = float(price)
                    price = "{:.2f}".format(float_value)
                except ValueError:
                    messages.error(request, "please enter a numerical value for price ")
                    url = reverse('update_product', kwargs={'product_id': product_id})
                    return redirect(url)
            
        new_category = Category.objects.get(id=category)

        product.name = product_name if product_name !="" else product.name
        product.hsn_code = hsn_code if hsn_code !="" else product.hsn_code
        product.tax_perc = tax_perc if tax_perc !="" else product.tax_perc
        product.price = price if price !="" else product.price
        product.remark = remarks if remarks !="" else product.remark
        product.category = new_category

        product.save()
        return redirect(reverse('product')+f'?page={page_number}')

        