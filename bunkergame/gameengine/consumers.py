# consumers.py

import json
from uuid import UUID

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from .models import GameEngine, GameUser
from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender=GameEngine)
def game_engine_updated(sender, instance:GameEngine, created, **kwargs):
    if not created:
        sync_game(instance.game_id)
        if instance.game_status == 4:
            send_info(instance.game_id, 'Началось голосование')
        if instance.game_status == 5:
            send_info(instance.game_id, 'Игра закончилась')

def send_game_message(game_id:UUID, message:dict, message_type:str='game_status'):
    channel_layer = get_channel_layer()
    room_group_name = f'game_{game_id}'

    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'game_status',
            'message': {**message, 'type': message_type}
        }
    )

def sync_game(game_id:UUID):
    try:
        game_engine = GameEngine.objects.get(game_id=game_id)
        game_users = GameUser.objects.filter(game_id=game_engine.game_id).all()

        send_game_message(game_id, {"game_users": [game_user.as_ru_dict() for game_user in game_users],
                                "game_info":{**game_engine.get_game_info()}})
    except Exception as e:
        print(f'cannot sync game {game_id}')


def send_info(game_id:UUID, message:str, error:bool=False):
    send_game_message(game_id, {'message':message, 'error':error}, 'game_info_message')

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = f'game_{self.game_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.close()

    async def game_status(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))