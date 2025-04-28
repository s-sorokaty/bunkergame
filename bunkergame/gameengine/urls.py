from django.urls import path
from .views import create_empty_game, game_list, join_game

app_name = 'gameengine'

urlpatterns = [
    path('create/', create_empty_game, name='create_game'),
    path('join/', join_game, name='join_game'),
    path('game_list/', game_list, name='game_list'),
]