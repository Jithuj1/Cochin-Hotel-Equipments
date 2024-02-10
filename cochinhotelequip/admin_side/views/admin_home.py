from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def admin_home_page(request):

    context = {'active_page': 'admin_home'}
    return render(request, 'admin/admin_home.html', context)
