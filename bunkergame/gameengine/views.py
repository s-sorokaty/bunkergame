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
        users_in_game = [game_user.account_id.username for game_user in GameUser.objects.filter(game_id=game_id).all()]
        user = User.objects.get(id=request.user.id)
        if not user.username in users_in_game: 
            game_engine.join_user(user)

        game_users = GameUser.objects.filter(game_id=game_engine.game_id).all()
        return render(request, "game.html", {"game_users": [game_user.as_ru_dict() for game_user in game_users],
                                             "game_info":{**game_engine.get_game_info(), "request_username":user.username},
                                             
                                             })
    return HttpResponseBadRequest("Wrong request method") 
       
@decorators.login_required(login_url='/accounts/login/')
def game_list(request:HttpRequest):
    games = GameEngine.objects.all().values()
    return JsonResponse(list(games), safe=False)

@decorators.login_required(login_url='/accounts/login/')
def start_game(request:HttpRequest, game_id:UUID):
    game_engine = GameEngine.objects.get(game_id=game_id)
    game_engine.start_game()

@decorators.login_required(login_url='/accounts/login/')
def leave_game(request:HttpRequest, game_id:UUID):
    game_engine = GameEngine.objects.get(game_id=game_id)
    game_engine.remove_user(request.user, )
    return redirect('/')