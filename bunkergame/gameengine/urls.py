from django.urls import path
from .views import create_empty_game, game_list, join_game, leave_game, start_game, show_stat, make_vote, retract_vote, end_vote, end_user_turn

app_name = 'gameengine'

urlpatterns = [
    path('create/', create_empty_game, name='create_game'),
    path('game_list/', game_list, name='game_list'),
    
    path('join/<uuid:game_id>', join_game, name='join_game'),
    path('leave/<uuid:game_id>', leave_game, name='leave_game'),
    path('start/<uuid:game_id>', start_game, name='start_game'),
    path('showstat/<uuid:game_id>/', show_stat, name='show_stat'),
    path('make_vote/<uuid:game_id>/', make_vote, name='make_vote'),
    path('end_user_turn/<uuid:game_id>/', end_user_turn, name='end_user_turn'),

    path('end_vote/<uuid:game_id>/', end_vote, name='end_vote'),
    path('retract_vote/<uuid:game_id>/', retract_vote, name='retract_vote'),

]