from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from account.models.user import User
from account.models.address import Address
from django.db.models import Q
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
import re


@login_required(login_url='login')
def customer(request):
    if request.method == 'GET':
        customers = User.objects.all().order_by("-date_joined")
    else:
        search = request.POST.get('search')
        search = search.strip()
        q_object = Q()
        q_object.add(Q(first_name__icontains=search), Q.OR)
        q_object.add(Q(last_name__icontains=search), Q.OR)
        q_object.add(Q(display_name__icontains=search), Q.OR)
        q_object.add(Q(username__icontains=search), Q.OR)
        q_object.add(Q(phone__icontains=search), Q.OR)

        customers = User.objects.filter(q_object).order_by("-date_joined")
    
    page = request.GET.get('page', 1)

    paginator = Paginator(customers, 25)
    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)

    context = {"customers": customers, "active_page":"customer"}
    return render(request, 'customer/customer.html', context)
    

@login_required(login_url='login')
def add_customer(request):
    if request.method == 'GET':
        context = {"active_page":"customer"}
        return render(request, 'customer/add_customer.html', context)
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        display_name = request.POST.get('display_name')
        gst_cus = request.POST.get('gst_cus')
        remarks = request.POST.get('remarks')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        street1 = request.POST.get('street1')
        street2 = request.POST.get('street2')
        pincode = request.POST.get('pincode')
        default_address = request.POST.get('default_address')
        address_type = request.POST.get('address_type')
        lan_mark = request.POST.get('lan_mark')

        if first_name == "" or phone == "" or pincode == "" or city =="" or street1 == "":
            messages.error(request, "first_name, phone and pincode can't be blank")
            return redirect('new_customer')
        if phone :
            phone_pattern = re.compile(r'^(\+91)?\d{10}$')

            if not phone_pattern.match(phone):
                messages.error(request, "phone number is not acceptable")
                return redirect('new_customer')

        try:
            with transaction.atomic():
                user = User.objects.create(
                    first_name = first_name,
                    last_name = last_name,
                    email = email,
                    phone = phone,
                    gst_cus = gst_cus,
                    remarks = remarks,
                    display_name = display_name,
                )

                address = Address.objects.create(
                    country = country,
                    state = state,
                    city = city,
                    street1 = street1,
                    street2 = street2,
                    is_default = default_address,
                    address_type = address_type,
                    lan_mark = lan_mark,
                    customer = user,
                    zipcode = pincode,
                    phone=phone

                )
                user.update_customer_details()
                address.update_customer_details()
                return redirect('customer')
        except Exception as e :
            messages.error(request, f"{e}")
 
        return render(request, 'customer/add_customer.html')
    

from django.http import HttpResponseBadRequest
from django.db.models.deletion import ProtectedError
@login_required(login_url='login')
def delete_customer(request, customer_id):
    try:
        page_number =  request.GET.get('page')
        User.objects.get(id=customer_id).delete()

    except ProtectedError:
        messages.warning(request, "Unable to delete this user because it's linked to invoice, please clear it's use first.")

    # return redirect('customer')
    return redirect(reverse('customer')+f'?page={page_number}')




@login_required(login_url='login')
def delete_address(request, address_id):
    page_number =  request.GET.get('page')

    address = Address.objects.get(id=address_id)
    other_address = Address.objects.filter(customer=address.customer).exclude(id=address_id).first()
    if not other_address:
        messages.error(request, "customer don't have any other address, please create one before deleting")
        url = reverse('view_customer', kwargs={'customer_id': address.customer.id}) +f'?page={page_number}'
        return redirect(url)
    
    if address.is_default:
        other_address.is_default = True
        other_address.save()
    try:
        address.delete()
    except ProtectedError:
        print(ProtectedError)
    print('page',page_number)
    url = reverse('view_customer', kwargs={'customer_id': address.customer.id}) +f'?page={page_number}'
    return redirect(url)

@login_required(login_url='login')
def view_customer(request, customer_id):
    # page number
    page_number =  request.GET.get('page')
    customer = User.objects.filter(id=customer_id).first()
    address_list = Address.objects.filter(customer = customer)
    context = {
        "customer":customer,
        "address_list":address_list,
        "active_page":"customer",
        'page_number': page_number
    }
    return render(request, 'customer/view_customer.html', context)


@login_required(login_url='login')
def add_address(request, customer_id):
    page_number =  request.GET.get('page')
    if request.method =="GET":
        context = {
        "customer":customer_id,
        "active_page":"customer",
        'page_number': page_number,
        }
        return  render(request, 'customer/add_address.html', context)
    else:
        phone = request.POST.get('phone')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        street1 = request.POST.get('street1')
        street2 = request.POST.get('street2')
        pincode = request.POST.get('pincode')
        default_address = request.POST.get('default_address')
        address_type = request.POST.get('address_type')
        lan_mark = request.POST.get('lan_mark')

        customer = User.objects.filter(id=customer_id).first()

        if phone == "" or pincode == "" or city =="" or street1 == "":
            messages.error(request, "street 1, city, phone and pincode can't be blank")
            url = reverse('add_address', kwargs={'customer_id': customer_id})+f'?page={page_number}'
            return redirect(url)
        if phone :
            phone_pattern = re.compile(r'^(\+91)?\d{10}$')

            if not phone_pattern.match(phone):
                messages.error(request, "phone number is not acceptable")
                url = reverse('add_address', kwargs={'customer_id': customer_id})+f'?page={page_number}'
                return redirect(url)
        try:
            with transaction.atomic():
                if default_address:
                    Address.objects.filter(customer=customer).update(is_default=False)
                
                address = Address.objects.create(
                    country = country,
                    state = state,
                    city = city,
                    street1 = street1,
                    street2 = street2,
                    is_default = default_address,
                    address_type = address_type,
                    lan_mark = lan_mark,
                    customer = customer,
                    zipcode = pincode,
                    phone=phone

                )
                address.update_customer_details()
                url = reverse('view_customer', kwargs={'customer_id': customer_id})+f'?page={page_number}'
                return redirect(url)
        except Exception as e :
            messages.error(request, f"{e}")


@login_required(login_url='login')
def update_customer(request, customer_id):
    page_number =  request.GET.get('page')

    customer = User.objects.filter(id=customer_id).first()
    context = {
        "customer":customer,
        "active_page":"customer",
        'page_number': page_number,

        }
    if request.method =="GET":
        
        return  render(request, 'customer/update_customer.html', context) 
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        display_name = request.POST.get('display_name') 
        remarks = request.POST.get('remarks')

        if any(value is not None and value.isspace() for value in [first_name, last_name, email, phone, display_name, remarks]):
            messages.error(request, "Input cannot be blank or None")
            url = reverse('update_customer', kwargs={'customer_id': customer_id})+f'?page={page_number}'
            return redirect(url)

        if phone :
            phone_pattern = re.compile(r'^(\+91)?\d{10}$')

            if not phone_pattern.match(phone):
                messages.error(request, "phone number is not acceptable")
                url = reverse('update_customer', kwargs={'customer_id': customer_id})+f'?page={page_number}'
                return redirect(url)
            
        customer.first_name = first_name if first_name != "" else customer.first_name
        customer.last_name = last_name if last_name != "" else customer.last_name
        customer.email = email if email != "" else customer.email
        customer.phone = phone if phone != "" else customer.phone
        customer.display_name = display_name if display_name != "" else customer.display_name
        customer.remarks = remarks if remarks != "" else customer.remarks

        customer.save()
        customer.update_customer_details()
        url = reverse('view_customer', kwargs={'customer_id': customer_id})+f'?page={page_number}'
        return redirect(url)
    

@login_required(login_url='login')
def update_address(request, address_id):
    page_number =  request.GET.get('page')

    address = Address.objects.filter(id=address_id).first()
    context = {
        "address":address,
        "active_page":"customer",
        'page_number': page_number,
        }
    if request.method =="GET":
        return  render(request, 'customer/update_address.html', context) 
    else:
        state = request.POST.get('state')
        city = request.POST.get('city')
        street1 = request.POST.get('street1')
        street2 = request.POST.get('street2')
        pincode = request.POST.get('pincode')
        default_address = request.POST.get('default_address')
        lan_mark = request.POST.get('lan_mark')
        phone = request.POST.get('phone')

        if any(value is not None and value.isspace() for value in [state, city, street1, street2, pincode, default_address, lan_mark, phone]):
            messages.error(request, "Input cannot be blank or None")
            url = reverse('update_address', kwargs={'address_id': address.id})
            return redirect(url)

        if phone :
            phone_pattern = re.compile(r'^(\+91)?\d{10}$')

            if not phone_pattern.match(phone.strip()):
                messages.error(request, "phone number is not acceptable")
                url = reverse('update_address', kwargs={'address_id': address.id})
                return redirect(url)
            
        try:
            with transaction.atomic():
                address.state = state if state !="" else address.state
                address.city = city if city !="" else address.city
                address.street1 = street1 if street1 !="" else address.street1
                address.street2 = street2 if street2 !="" else address.street2
                address.zipcode = pincode if pincode !="" else address.zipcode
                address.is_default = default_address if default_address !="" else address.is_default
                address.lan_mark = lan_mark if lan_mark !="" else address.lan_mark
                address.phone = phone if phone !="" else address.phone

                address.save()
                address.update_customer_details()
                if default_address:
                    Address.objects.filter(customer=address.customer).exclude(id=address.id).update(is_default=False)
        except Exception as e :
            messages.error(request, f"{e}")
            url = reverse('update_address', kwargs={'address_id': address.id})
            return redirect(url)

        url = reverse('view_customer', kwargs={'customer_id': address.customer.id})+f'?page={page_number}'
        return redirect(url)
           
