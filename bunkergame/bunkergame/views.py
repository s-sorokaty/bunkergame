from django import http
from django.shortcuts import render

def error_404(request: http.HttpRequest, exception):
    context = {}
    return render(request, '404.html', context, status=404)

def error_500(request):
   context = {}
   return render(request,'404.html', context)