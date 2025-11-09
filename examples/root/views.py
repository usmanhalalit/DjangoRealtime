from django.shortcuts import render


def index(request):
    """Homepage showing list of example apps"""
    return render(request, 'root/index.html')
