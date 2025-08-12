import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.middleware.csrf import CsrfViewMiddleware

from .models import Chat, Message, STATUS
from channels.db import database_sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # Get connection parameters
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.receiver_id = self.scope['url_route']['kwargs']['receiver_id']

            # Get user from scope
            self.user = self.scope["user"]

            logger.info(
                f"WebSocket connection attempt - User: {self.user}, Room: {self.room_name}, Receiver: {self.receiver_id}")

            # Verify authentication
            if isinstance(self.user, AnonymousUser):
                logger.warning("WebSocket connection rejected: User not authenticated")
                await self.close(code=4001)  # Unauthorized
                return

            # Get token from query parameters
            query_string = self.scope.get('query_string', b'').decode('utf-8')
            query_params = dict(
                pair.split('=') for pair in query_string.split('&') if '=' in pair
            )
            token = query_params.get('token', '')

            # Verify CSRF token
            if not token or not await self.verify_csrf_token(token):
                logger.warning("WebSocket connection rejected: Invalid CSRF token")
                await self.close(code=4003)  # Forbidden
                return

            # Get receiver
            self.receiver = await self.get_receiver()
            if not self.receiver:
                logger.warning(f"Receiver not found: {self.receiver_id}")
                await self.close(code=4004)  # Not found
                return

            # Get room
            self.room = await self.get_room()
            if not self.room:
                logger.warning(f"Room not found: {self.room_name}")
                await self.close(code=4004)  # Not found
                return

            # Accept connection
            await self.accept()

            # Set up room group
            self.room_group_name = f'chat_{self.room_name}'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            logger.info(f"WebSocket connection established - User: {self.user}, Room: {self.room_name}")

            # Send handshake confirmation
            await self.send(text_data=json.dumps({
                'type': 'handshake_complete',
                'status': 'success',
                'user_id': str(self.user.id),
                'room_name': self.room_name
            }))

        except Exception as e:
            logger.error(f"WebSocket connection error: {str(e)}", exc_info=True)
            try:
                await self.send(text_data=json.dumps({
                    'type': 'handshake_failed',
                    'error': str(e)
                }))
            except:
                pass
            await self.close(code=4000)  # Bad request

    @database_sync_to_async
    def verify_csrf_token(self, token):
        """Verify CSRF token with better error handling"""
        try:
            from django.middleware.csrf import CsrfViewMiddleware
            from django.http import HttpRequest

            request = HttpRequest()
            request.method = 'POST'
            request.META = {
                'HTTP_X_CSRFTOKEN': token,
                'CSRF_COOKIE': token,
            }

            middleware = CsrfViewMiddleware(lambda x: None)
            middleware.process_request(request)
            return True
        except Exception as e:
            logger.error(f"CSRF verification failed: {str(e)}")
            return False

    @database_sync_to_async
    def get_message_history(self, room, last_message_id=0):
        messages = Message.active_messages.filter(
            chat=room,
            id__gt=last_message_id
        ).order_by('date_created')
        return [
            {
                'author__username': msg.author.username,
                'author_id': msg.author.id,
                'message': msg.message,
                'date_created': msg.date_created.isoformat(),
                'id': msg.pkid
            }
            for msg in messages
        ]

    @database_sync_to_async
    def get_receiver(self):
        """Get receiver user object"""
        try:
            return get_user_model().objects.get(id=self.receiver_id)
        except (get_user_model().DoesNotExist, ValueError) as e:
            logger.error(f"Receiver not found: {self.receiver_id} - {str(e)}")
            return None

    @database_sync_to_async
    def get_room(self):
        """Get chat room with better error handling"""
        try:
            return Chat.active_chats.get(slug=self.room_name)
        except Chat.DoesNotExist:
            logger.error(f"Chat room not found: {self.room_name}")
            return None
        except Exception as e:
            logger.error(f"Error getting chat room {self.room_name}: {str(e)}")
            return None

    @database_sync_to_async
    def save_message(self, room, content):
        return Message._default_manager.create(
            chat=room,
            author=self.user,
            sent_for=self.receiver,
            message=content,
            status=STATUS.SENT
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
            message.status = STATUS.EDITED
            message.date_updated = timezone.now()
            message.save()

            # Return the updated message
            return {
                'id': message.pkid,
                'message': message.message,
                'date_updated': message.date_updated,
                'author_id': message.author.id
            }

        except Message.DoesNotExist:
            raise ValueError("Message not found")
        except Exception as e:
            print(f"Error updating message: {str(e)}")
            raise

    @database_sync_to_async
    def delete_message(self, message_id):
        try:
            # Use default manager instead of active_messages to ensure we can find the message
            message = Message.objects.get(pkid=message_id)

            if not message:
                logger.error("Message not found")
                raise ValueError("Message not found")
            
            # Verify ownership
            if message.author.id != self.user.id:
                raise PermissionError("You can only delete your own messages")

            # Delete message
            message.status = STATUS.DELETED
            message.delete() # Soft delete

        except Message.DoesNotExist:
            logger.error("Message not found")
        except Exception as e:
            logger.error(f"Error deleting message: {str(e)}")
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
                            'date_updated': update_result['date_updated'].isoformat(),
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
            'date_updated': event['date_updated']
        }))