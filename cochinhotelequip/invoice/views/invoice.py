from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from invoice.models.invoice import Invoice, InvoiceItem, StoreNames
from product.models.product import Product
from django.db.models import Q
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required(login_url='login')
def invoice(request):
    if request.method == 'GET':
        Invoice.objects.filter(sub_total = 0, amount_paid=0).delete()
        invoice_list = Invoice.objects.filter(is_quotation=False).order_by('-created_at')
    else:
        search = request.POST.get('search')
        search = search.strip()
        if search.count("/") == 3 :
            qtn_no = search.split("/")
            fiscal_year = qtn_no[-2]
            seq_no = qtn_no[-1]
            invoice_list = Invoice.objects.filter(
            Q(is_quotation=True) &
            (Q(invoice_num_fiscalyr=fiscal_year)) & 
            (Q(invoice_num_seq=seq_no))  
            ).order_by('-created_at')
        else:
            invoice_list = Invoice.objects.filter(Q(is_quotation=False))
            words = search.split()
    
            if search.isdigit() or (search.replace('.', '', 1).isdigit() and search.count('.') == 1):
                invoice_list = invoice_list.filter(
                    Q(sub_total__exact=search) |
                    Q(grand_total__exact=search)
                )
            else:
                for word in words:
                    invoice_list = invoice_list.filter(
                        Q(customer__first_name__icontains=word) |
                        Q(customer__last_name__icontains=word) |
                        Q(quotation_date__icontains=word)
                    )

            invoice_list = invoice_list.order_by('-created_at')


    page = request.GET.get('page', 1)

    paginator = Paginator(invoice_list, 15)
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
    products = Product.objects.all().order_by('-created_at')

    recent_product = InvoiceItem.objects.order_by('product_id', '-created_at').distinct('product_id')[:6]

    invoice_items = InvoiceItem.objects.filter(invoice=invoice)
    page_number = request.GET.get('page')
    if request.method == "POST":
        unit = request.POST.get('productName')
        if not unit:
            messages.error(request, 'Please choose a product.')
           
        product = Product.objects.get(id=unit)
        existing_quotation_item = InvoiceItem.objects.filter(
            invoice=invoice_id, product=product)

        if existing_quotation_item:
            quotation_item = existing_quotation_item.first()
            quotation_item.qty += 1
        else:
            quotation_item = InvoiceItem(
                product=product,
                invoice=invoice,
                rate=product.price,
                qty=1
            )
        quotation_item.save()
        quotation_item.calculate_item_totals()
        quotation_item.invoice.calculate_total()
        return redirect('view_invoice', invoice_id)
    
    context = {
        "invoice": invoice,
        'products': products,
        "invoice_items": invoice_items,
        "address": invoice.address,
        "recent_product": recent_product,
        "active_page":"invoice",
        "page":page_number,
    }

    return render(request, 'invoice/invoice_detail.html', context)


@login_required(login_url='login')
def add_discount(request, invoice_id):
    if request.method == 'POST':

        discount = request.POST.get('discount')
        discount = int(discount.split(".")[0])

        invoice = Invoice.objects.get(id=invoice_id)
        if discount > invoice.amount_remaining:
            messages.error(request, "You can't provide discount more than amount remaining")
            return redirect('view_invoice', invoice_id)
        invoice.discount = discount
        invoice.save()
        
        invoice.calculate_total()

        return redirect('view_invoice', invoice_id)
    

@login_required(login_url='login')
def make_payment(request, invoice_id):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        amount = amount.split(".")[0]
        page_number = request.GET.get('page')

        invoice = Invoice.objects.get(id=invoice_id)

        response = invoice.make_payment(int(amount))

        if not response["status"] :
            messages.warning(request, response["message"])
            return redirect(reverse('invoice')+f'?page={page_number}')
        
        return redirect(reverse('invoice')+f'?page={page_number}')
    

@login_required(login_url='login')
def delete_invoice(request, invoice_id):
    InvoiceItem.objects.filter(invoice=invoice_id).delete()
    Invoice.objects.get(id=invoice_id).delete()
    return redirect('invoice')


@login_required(login_url='login')
def edit_invoice_item(request, invoice_id, invoice_item_id):
    if request.method == 'POST':

        quantity = int(request.POST.get('quantity'))
        rate = float(request.POST.get('rate'))

        invoice_item = InvoiceItem.objects.get(id=invoice_item_id)
        invoice_item.qty = quantity
        invoice_item.rate = rate
        invoice_item.save()

        invoice_item.calculate_item_totals()
        invoice_item.invoice.calculate_total()

        return redirect('view_invoice', invoice_id)


@login_required(login_url='login')
def delete_invoice_product(requset, invoice_id, invoice_item_id):
    invoice_item = InvoiceItem.objects.get(id=invoice_item_id)
    invoice = invoice_item.invoice
    invoice_item.delete()
    invoice.discount = 0
    invoice.save()

    invoice.calculate_total()
    return redirect('view_invoice', invoice_id)