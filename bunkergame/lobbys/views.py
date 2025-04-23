from django import http
from django.shortcuts import render
from django.contrib.auth import authenticate, login, decorators 

@decorators.login_required(login_url='/accounts/login/')
def get_lobbys_list(request: http.HttpRequest):
    return render(request, 'lobbys.html')