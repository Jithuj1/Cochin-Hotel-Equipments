from django.shortcuts import render


def home_page(request):
    context = {'message': 'Hello, this is your Django app!'}
    return render(request, 'home/home.html', context)