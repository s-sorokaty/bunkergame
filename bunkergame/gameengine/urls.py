from django.urls import path
from django.urls import re_path
from .views import create_empty_game, game_list, join_game, leave_game, start_game

app_name = 'gameengine'

urlpatterns = [
    path('create/', create_empty_game, name='create_game'),
    path('game_list/', game_list, name='game_list'),
    
    path('join/<str:game_id>', join_game, name='join_game'),
    path('leave/<str:game_id>', leave_game, name='leave_game'),
    path('start/<str:game_id>', start_game, name='start_game'),

]