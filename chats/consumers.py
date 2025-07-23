import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
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

        try:
            self.receiver = await self.get_receiver()
            if not self.receiver:
                await self.close()
                return

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            # Get or create room and history
            room = await self.get_or_create_room()
            history = await self.get_message_history(room)

            # Send history as separate messages
            for message in history:
                await self.send(text_data=json.dumps({
                    'type': 'chat_message',
                    'message': message['message'],
                    'sender': message['author__username'],
                    'timestamp': message['created_at']
                }))

        except Exception as e:
            print(f"Connection error: {str(e)}")
            await self.close()

    @database_sync_to_async
    def get_message_history(self, room):
        messages = Message.objects.filter(chat=room).order_by('created_at')
        return [
            {
                'author__username': msg.author.username,
                'message': msg.message,
                'created_at': msg.created_at.isoformat()
            }
            for msg in messages
        ]

    @database_sync_to_async
    def get_receiver(self):
        try:
            return get_user_model().objects.get(id=self.receiver_id)
        except (get_user_model().DoesNotExist, ValueError):
            return None

    @database_sync_to_async
    def get_or_create_room(self):
        room, created = Chat.objects.get_or_create(
            slug=self.room_name,
            author=self.user,
            chat_to_user=self.receiver,
        )
        return room

    @database_sync_to_async
    def save_message(self, room, content):
        Message.objects.create(
            chat=room,
            author=self.user,
            sent_for=self.receiver,
            message=content,
        )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message', '').strip()

            if not message:
                return

            if not isinstance(self.user, AnonymousUser):
                room = await self.get_or_create_room()
                await self.save_message(room, message)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'sender': self.user.username,
                        'timestamp': timezone.now().isoformat()
                    }
                )
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to process message'
            }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))