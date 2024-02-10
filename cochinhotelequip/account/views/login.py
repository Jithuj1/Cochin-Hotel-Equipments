from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('admin_home') 
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'admin/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')  