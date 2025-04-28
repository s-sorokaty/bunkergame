from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, decorators 
from django.http import JsonResponse, HttpRequest, HttpResponseBadRequest

from .models import GameEngine

@decorators.login_required(login_url='/accounts/login/')
def create_empty_game(request:HttpRequest):
    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)
        game_engine = GameEngine()
        game_name = request.POST['game_name']
        user_count = request.POST['user_count']
        game_engine.create_empty_game(user, game_name, user_count)
        return JsonResponse({'game_id':game_engine.game_id}, safe=False)
    else: return HttpResponseBadRequest("Wrong request method") 

@decorators.login_required(login_url='/accounts/login/')
def join_game(request:HttpRequest):
    pass
       

@decorators.login_required(login_url='/accounts/login/')
def game_list(request:HttpRequest):
    games = GameEngine.objects.all().values()
    return JsonResponse(list(games), safe=False)