from uuid import UUID
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, decorators
from django.http import JsonResponse, HttpRequest, HttpResponseBadRequest

from .models import GameEngine, GameUser
from .consumers import send_game_message
from .utils import exceptions

def sync_game(request, game_id:UUID):
    game_engine = GameEngine.objects.get(game_id=game_id)
    game_users = GameUser.objects.filter(game_id=game_engine.game_id).all()
    user = User.objects.get(id=request.user.id)

    send_game_message(game_id, {"game_users": [game_user.as_ru_dict() for game_user in game_users],
                                "game_info":{**game_engine.get_game_info(), "request_username":user.username}})

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
        try:
            game_engine = GameEngine.objects.get(game_id=game_id)
            users_in_game = [game_user.account_id.username for game_user in GameUser.objects.filter(game_id=game_id).all()]
            user = User.objects.get(id=request.user.id)
            if not user.username in users_in_game: 
                game_engine.join_user(user)
            
            game_users = GameUser.objects.filter(game_id=game_engine.game_id).all()
        
            sync_game(request, game_id)
            return render(request, "game.html", {"game_users": [game_user.as_ru_dict() for game_user in game_users],
                                             "game_info":{**game_engine.get_game_info(), "request_username":user.username},
                                             
                                             })
        except exceptions.LobbyStatusCheckMismatch:
            return redirect('/')


    return HttpResponseBadRequest("Wrong request method") 
       
@decorators.login_required(login_url='/accounts/login/')
def game_list(request:HttpRequest):
    games = GameEngine.objects.all().values()
    return JsonResponse(list(games), safe=False)

@decorators.login_required(login_url='/accounts/login/')
def start_game(request:HttpRequest, game_id:UUID):
    try:
        game_engine = GameEngine.objects.get(game_id=game_id)
        game_engine.start_game()
        return JsonResponse({'message':'Игра началась'}, status=200)
    except exceptions.LobbyStatusCheckMismatch as e:
        return JsonResponse({'err':'Не получилось начать игру, возможно игра уже запущена или недостаточно игроков'}, status=404)


@decorators.login_required(login_url='/accounts/login/')
def show_stat(request:HttpRequest, game_id:UUID):
    statname = request.GET.get("statname")
    game_engine = GameEngine.objects.get(game_id=game_id)
    user = User.objects.get(id=request.user.id)
    game_user = GameUser.objects.filter(game_id=game_engine.game_id, account_id=user).first()
    game_user.show_stat(statname)
    sync_game(request, game_id)
    return JsonResponse(list([]), safe=False)

@decorators.login_required(login_url='/accounts/login/')
def leave_game(request:HttpRequest, game_id:UUID):
    game_engine = GameEngine.objects.get(game_id=game_id)
    game_engine.remove_user(request.user, )
    sync_game(request, game_id)
    return redirect('/')