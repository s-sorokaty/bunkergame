from uuid import UUID
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, decorators
from django.http import JsonResponse, HttpRequest, HttpResponseBadRequest

from .models import GameEngine, GameUser
from .consumers import sync_game, send_info
from .utils import exceptions

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
        
            sync_game(game_id)
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
        user = User.objects.get(id=request.user.id)
        game_user = GameUser.objects.filter(game_id=game_engine.game_id, account_id=user).first()
        if not game_user.is_in_game: raise exceptions.KickedUser
        if game_user.account_id != game_engine.owner_id: raise exceptions.OnlyOwner

        game_engine.start_game()
        send_info(game_engine.game_id, 'Игра началась')
        sync_game(game_id)
        return JsonResponse({'message':'Игра началась'}, status=200)
    except exceptions.KickedUser:
        return JsonResponse({'err':'Вы выбыли из убежища'}, status=400)
    except exceptions.LobbyStatusCheckMismatch as e:
        return JsonResponse({'err':'Не получилось начать игру, возможно игра уже запущена или недостаточно игроков'}, status=400)
    except exceptions.OnlyOwner as e:
        return JsonResponse({'err':'Только владелец комнаты может начать игру'}, status=400)

@decorators.login_required(login_url='/accounts/login/')
def show_stat(request:HttpRequest, game_id:UUID):
    statname = request.GET.get("statname")
    game_engine = GameEngine.objects.get(game_id=game_id)
    user = User.objects.get(id=request.user.id)
    game_user = GameUser.objects.filter(game_id=game_engine.game_id, account_id=user).first()
    try:
        if not game_user.is_in_game: raise exceptions.KickedUser
        game_engine.show_stat(statname, game_user)
        sync_game(game_id)
        return JsonResponse({'message':'Вы показали свою характеристику'}, status=200)
    except exceptions.KickedUser:
        return JsonResponse({'err':'Вы выбыли из убежища'}, status=400)
    except exceptions.LobbyStatusCheckMismatch:
        return JsonResponse({'err':'Сейчас нельзя показывать карту'}, status=400)
    except exceptions.WrongPlayerTurn:
        return JsonResponse({'err':'Сейчас не ваш ход'}, status=400)
    except exceptions.StatAlreadyShowed:
        return JsonResponse({'err':'Вы уже показали эту карту'}, status=400)

@decorators.login_required(login_url='/accounts/login/')
def make_vote(request:HttpRequest, game_id:UUID):
    vote_user_id = request.GET.get("vote_user_id")
    game_engine = GameEngine.objects.get(game_id=game_id)
    user = User.objects.get(id=request.user.id)
    game_user = GameUser.objects.get(game_id=game_engine.game_id, account_id=user)
    
    try:
        if not game_user.is_in_game: raise exceptions.KickedUser
        game_engine.make_vote(game_user, vote_user_id)
        sync_game(game_id)
        return JsonResponse({'message':'Вы проголосовали'}, status=200)
    except exceptions.KickedUser:
        return JsonResponse({'err':'Вы выбыли из убежища'}, status=400)
    except exceptions.LobbyStatusCheckMismatch:
        return JsonResponse({'err':'Сейчас нельзя голосовать'}, status=400)

@decorators.login_required(login_url='/accounts/login/')
def end_vote(request:HttpRequest, game_id:UUID):
    game_engine = GameEngine.objects.get(game_id=game_id)
    user = User.objects.get(id=request.user.id)
    game_user = GameUser.objects.get(game_id=game_engine.game_id, account_id=user)
    try:
        if not game_user.is_in_game: raise exceptions.KickedUser
        if game_user.account_id != game_engine.owner_id: raise exceptions.OnlyOwner
        game_engine.end_vote()
        sync_game(game_id)
        return JsonResponse({'message':'Голосование закончено'}, status=200)
    except exceptions.KickedUser:
        return JsonResponse({'err':'Вы выбыли из убежища'}, status=400)
    except exceptions.LobbyStatusCheckMismatch:
        return JsonResponse({'err':'Сейчас нет голосования'}, status=400)
    except exceptions.OnlyOwner as e:
        return JsonResponse({'err':'Только владелец комнаты может закончить голосование'}, status=400)

@decorators.login_required(login_url='/accounts/login/')
def retract_vote(request:HttpRequest, game_id:UUID):
    game_engine = GameEngine.objects.get(game_id=game_id)
    user = User.objects.get(id=request.user.id)
    game_user = GameUser.objects.get(game_id=game_engine.game_id, account_id=user)
    
    try:
        if not game_user.is_in_game: raise exceptions.KickedUser
        game_engine.make_vote(game_user, None)
        sync_game(game_id)
        return JsonResponse({'message':'Вы убрали голос'}, status=200)
    except exceptions.KickedUser:
        return JsonResponse({'err':'Вы выбыли из убежища'}, status=400)
    except exceptions.LobbyStatusCheckMismatch:
        return JsonResponse({'err':'Сейчас нельзя голосовать'}, status=400)

@decorators.login_required(login_url='/accounts/login/')
def leave_game(request:HttpRequest, game_id:UUID):
    game_engine = GameEngine.objects.get(game_id=game_id)
    game_engine.remove_user(request.user, )
    sync_game(game_id)
    return redirect('/')