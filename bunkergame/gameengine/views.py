from uuid import UUID
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, decorators
from django.http import JsonResponse, HttpRequest, HttpResponseBadRequest

from .models import GameEngine, GameUser

@decorators.login_required(login_url='/accounts/login/')
def create_empty_game(request:HttpRequest):
    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)
        game_engine = GameEngine()
        game_name = request.POST['game_name']
        user_count = request.POST['user_count']
        game_engine.create_empty_game(user, game_name, user_count)
        return redirect(f"/game/join/{game_engine.game_id}")
    else: return HttpResponseBadRequest("Wrong request method") 

@decorators.login_required(login_url='/accounts/login/')
def join_game(request:HttpRequest, game_id:UUID):
    if request.method == 'GET':
        game_engine = GameEngine.objects.get(game_id=game_id) 
        game_user = User.objects.get(id=request.user.id)
        game_engine.join_user(game_user)
        game_users = GameUser.objects.filter(game_id=game_engine.game_id).all()

        #user = User.objects.get(id=request.user.id)
        #game_engine = GameEngine()
        #game_name = request.GET['game_id']
        return render(request, "game.html", {"game_users": [game_user.as_ru_dict() for game_user in game_users],
                                             "bunker_description":game_engine.get_ru_bunker_descriptions(),
                                             "map_description":game_engine.get_ru_map_descriptions()
                                             })
    return HttpResponseBadRequest("Wrong request method") 
       

@decorators.login_required(login_url='/accounts/login/')
def game_list(request:HttpRequest):
    games = GameEngine.objects.all().values()
    return JsonResponse(list(games), safe=False)