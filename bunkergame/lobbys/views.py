from django import http
from django.shortcuts import render
from django.contrib.auth import authenticate, login, decorators 
from gameengine.models import GameEngine


@decorators.login_required(login_url='/accounts/login/')
def get_lobbys_list(request: http.HttpRequest):
    games = GameEngine.objects.all().values()
    return render(request, 'lobbys.html', {'lobbies': games})