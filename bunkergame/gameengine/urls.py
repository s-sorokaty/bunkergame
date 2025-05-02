from django.urls import path
from .views import create_empty_game, game_list, join_game, leave_game, start_game, show_stat

app_name = 'gameengine'

urlpatterns = [
    path('create/', create_empty_game, name='create_game'),
    path('game_list/', game_list, name='game_list'),
    
    path('join/<uuid:game_id>', join_game, name='join_game'),
    path('leave/<uuid:game_id>', leave_game, name='leave_game'),
    path('start/<uuid:game_id>', start_game, name='start_game'),
    path('showstat/<uuid:game_id>/', show_stat, name='show_stat'),

]