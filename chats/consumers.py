import json
from datetime import timezone

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from .models import Chat, Message
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.receiver_id = self.scope['url_route']['kwargs']['receiver_id']
        self.room_group_name = f'chat_{self.room_name}_{self.receiver_id}'
        self.user = self.scope['user']

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Save message to database
        if not isinstance(self.user, AnonymousUser):
            room = self.get_or_create_room()
            self.save_message(room, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username if not isinstance(self.user, AnonymousUser) else 'Anonymous',
                'timestamp': str(timezone.now())
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def get_or_create_room(self):
        room, created = Chat.objects.get_or_create(name=self.room_name,
                                                   author=self.user,
                                                   chat_to_user__id=self.receiver_id)
        # if created and not isinstance(self.user, AnonymousUser):
        #     room.participants.add(self.user)
        return room

    # @database_sync_to_async
    # def get_message_history(self, room):
    #     return list(Message.objects.filter(room=room)
    #                 .order_by('timestamp')
    #                 .values('sender__username', 'content', 'timestamp'))

    @database_sync_to_async
    def save_message(self, room, content):
        if not isinstance(self.user, AnonymousUser):
            Message.objects.create(
                chat=room,
                author=self.user,
                message=content,
                chat_to_user__id=self.receiver_id
            )