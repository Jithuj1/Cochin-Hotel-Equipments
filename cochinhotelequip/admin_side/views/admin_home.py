from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from invoice.models.invoice import Invoice
from datetime import datetime, timedelta
from django.utils import timezone
from invoice.utils.financial_year import fiscal_year_4digit
from django.db.models.functions import TruncMonth


@login_required(login_url='login')
def admin_home_page(request):
    financial_year = fiscal_year_4digit()
    current_date = datetime.now()

    today_invoice_list = Invoice.objects.filter(
        is_quotation = False,
        invoice_date = datetime.today())
    
    amount_remaining_list = Invoice.objects.filter(
        is_quotation = False,
        amount_remaining__gt=0)
    
    total_revenue = Invoice.objects.filter(
        is_quotation = False)
    
    recent_inovice = Invoice.objects.filter(is_quotation = False).order_by("-invoice_date", "-created_at")[:7]
    
    invoices_current_month = Invoice.objects.annotate(
    truncated_month=TruncMonth('invoice_date')).filter(
        is_quotation=False,
        truncated_month__month=current_date.month,
        truncated_month__year=current_date.year
    )

    today_sale_in_ekm = today_sale_in_tsr = 0
    amount_remaining_ekm = amount_remaining_tsr = 0
    total_revenue_ekm = total_revenue_tsr = 0
    last_month_revenue_ekm = last_month_revenue_tsr = 0

    for invoice in today_invoice_list:
        if invoice.store == "ERNAKULAM":
            today_sale_in_ekm +=invoice.grand_total
        else : today_sale_in_tsr +=invoice.grand_total

    for invoice in amount_remaining_list:
        if invoice.store == "ERNAKULAM":
            amount_remaining_ekm +=invoice.amount_remaining
        else : amount_remaining_tsr +=invoice.amount_remaining

    for invoice in total_revenue:
        if invoice.store == "ERNAKULAM":
            total_revenue_ekm +=invoice.grand_total
        else : total_revenue_tsr +=invoice.grand_total

    for invoice in invoices_current_month:
        if invoice.store == "ERNAKULAM":
            last_month_revenue_ekm +=invoice.grand_total
        else : last_month_revenue_tsr +=invoice.grand_total

    context = {
        'active_page': 'admin_home',
        "financial_year": financial_year[:2] + "-" + financial_year[2:],
        "current_month":current_date.strftime('%b'),
        "today_sale_in_ekm":int(today_sale_in_ekm),
        "today_sale_in_tsr":int(today_sale_in_tsr),
        "amount_remaining_ekm":int(amount_remaining_ekm),
        "amount_remaining_tsr":int(amount_remaining_tsr),
        "total_revenue_ekm":int(total_revenue_ekm),
        "total_revenue_tsr":int(total_revenue_tsr),
        "last_month_revenue_ekm":int(last_month_revenue_ekm),
        "last_month_revenue_tsr":int(last_month_revenue_tsr),
        "recent_inovice":recent_inovice,
        }
    
    return render(request, 'admin/admin_home.html', context)
