import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.middleware.csrf import CsrfViewMiddleware

from .models import Chat, Message
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # Get connection parameters
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.receiver_id = self.scope['url_route']['kwargs']['receiver_id']

            # Verify authentication
            if isinstance(self.scope["user"], AnonymousUser):
                await self.close(code=4001)
                return

            # Verify CSRF token from query string
            token = self.scope["query_string"].decode().split('token=')[1]
            if not await self.verify_csrf_token(token):
                await self.close(code=4003)
                return

            # Accept connection first
            await self.accept()

            # Complete handshake
            self.room_group_name = f'chat_{self.room_name}_{self.receiver_id}'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.send(json.dumps({
                'type': 'handshake_complete',
                'status': 'success',
                'user_id': str(self.scope["user"].id)
            }))

        except Exception as e:
            await self.send(json.dumps({
                'type': 'handshake_failed',
                'error': str(e)
            }))
            await self.close(code=4002)

    @database_sync_to_async
    def verify_csrf_token(self, token):
        middleware = CsrfViewMiddleware()
        request = type('Request', (), {
            'COOKIES': {settings.CSRF_COOKIE_NAME: token},
            'method': 'POST',
            'META': {}
        })
        try:
            middleware.process_request(request)
            return True
        except:
            return False

    @database_sync_to_async
    def get_message_history(self, room, last_message_id=0):
        messages = Message.active_messages.filter(
            chat=room,
            id__gt=last_message_id
        ).order_by('created_at')
        return [
            {
                'author__username': msg.author.username,
                'author_id': msg.author.id,  # Add author ID
                'message': msg.message,
                'created_at': msg.created_at.isoformat(),
                'id': msg.pkid
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
    def get_room(self):
        room = Chat.active_chats.get(
            slug=self.room_name
        )
        return room

    @database_sync_to_async
    def save_message(self, room, content):
        return Message._default_manager.create(
            chat=room,
            author=self.user,
            sent_for=self.receiver,
            message=content,
        )

    @database_sync_to_async
    def update_message(self, message_id, new_content):
        try:
            # Use default manager instead of active_messages to ensure we can find the message
            message = Message.objects.get(pkid=message_id)

            # Verify ownership
            if message.author.id != self.user.id:
                raise PermissionError("You can only edit your own messages")

            # Update message
            message.message = new_content
            message.updated_at = timezone.now()
            message.save()

            # Return the updated message
            return {
                'id': message.pkid,
                'message': message.message,
                'updated_at': message.updated_at,
                'author_id': message.author.id
            }

        except Message.DoesNotExist:
            raise ValueError("Message not found")
        except Exception as e:
            print(f"Error updating message: {str(e)}")
            raise

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            if data.get('type') == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'message': 'Connection confirmed'
                }))
                return

            message_type = data.get('type', 'chat_message')

            if message_type == 'edit_message':
                message_id = data.get('message_id')
                new_content = data.get('new_content', '').strip()

                if not new_content:
                    return

                try:
                    # Update message in database
                    update_result = await self.update_message(message_id, new_content)

                    # Broadcast update to all clients
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'message_edited',
                            'message_id': update_result['id'],
                            'new_content': update_result['message'],
                            'sender': self.user.username,
                            'updated_at': update_result['updated_at'].isoformat(),
                            'author_id': update_result['author_id']
                        }
                    )

                    # Send confirmation to sender
                    await self.send(text_data=json.dumps({
                        'type': 'edit_success',
                        'message_id': update_result['id']
                    }))

                except ValueError as e:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': str(e)
                    }))
                except PermissionError as e:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': str(e)
                    }))
                except Exception as e:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'Failed to update message'
                    }))

        except Exception as e:
            print(f"Error processing message: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to process message'
            }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
            'id': event['id'],
            'author_id': event['author_id']
        }))

    async def message_edited(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_edited',
            'message_id': event['message_id'],
            'new_content': event['new_content'],
            'sender': event['sender'],
            'updated_at': event['updated_at']
        }))