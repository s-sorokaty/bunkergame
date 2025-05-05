# consumers.py

import json
from uuid import UUID

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_game_message(game_id:UUID, message:dict):
    channel_layer = get_channel_layer()
    room_group_name = f'game_{game_id}'

    # Отправка сообщения в группу
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'game_status',
            'message': {**message, 'type': 'game_status'}
        }
    )
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