import logging
from typing import Union

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse

from .models import Chat, Message


logger = logging.getLogger(__name__)

class GetChatObjectMixin():
    def get_object(self):
        _slug = self.kwargs.get(self.slug_field, '')
        try:
            chat = get_object_or_404(Chat, slug=_slug)
        except Chat.DoesNotExist:
            chat = None
        return chat

class GetMessageObjectMixin():
    def get_object(self):
        _uuid = self.kwargs.get('pk', '')
        try:
            message = get_object_or_404(Message, id=_uuid)
        except Message.DoesNotExist:
            message = None
        return message

class BaseChatMessageMixin:
    _access_forbidden_url = reverse_lazy("exceptions:403_access_forbidden")

    def chat_exists(self,
                                       request,
                                       chat:Union[Chat, None],
                                       chat_slug: str,
                                       ) -> bool:
        if chat is None:
            messages.error(request, 'Chat does not exist!')
            return False
        return True

    def can_access_chat(self, request, chat: Union[Chat, None]) -> bool:
        if chat is None:
            logger.debug("Chat is None in can_access_chat")
            return False

        logger.debug(f"Checking access for user {request.user.id} against chat {chat.id}")
        logger.debug(f"Chat author: {chat.author.id}, Chat recipient: {chat.chat_to_user.id}")

        has_access = request.user in [chat.author, chat.chat_to_user]
        logger.debug(f"Access granted: {has_access}")

        return has_access

class ChatAccessPermissionRequiredMixin(BaseChatMessageMixin):
    def get(self, request, *args, **kwargs):
        chat = self.get_object()
        _chat_slug = self.kwargs.get(self.slug_field, "")

        logger.debug(f"Chat object: {chat}")
        logger.debug(f"Request user: {request.user}")

        if not self.chat_exists(request, chat, _chat_slug):
            logger.error(f'Chat does not exist! Chat: {chat}')
            messages.error(request, 'Chat does not exist!')
            return redirect(reverse('chats:user-chats', kwargs={'chat_slug': _chat_slug}))

        if not self.can_access_chat(request, chat):
            logger.error(f'Access denied for user {request.user} to chat {chat}')
            return redirect(self._access_forbidden_url)

        return super().get(request, *args, **kwargs)

class MessageAccessPermissionRequiredMixin(BaseChatMessageMixin):
    def get(self, request, *args, **kwargs):
        message: Union[Message, None] = self.get_object()
        _chat_slug = self.kwargs.get(self.slug_field, "")

        if message.chat is None:
            logger.error(f'Chat does not exist!')

            messages.error(request, 'Chat does not exist!')
            return redirect(reverse('chats:user-chats', kwargs={'chat_slug': _chat_slug}))

        if message is None:
            logger.error(f'Message does n')

            messages.error(request, 'Message does not exist!')
            return redirect(reverse('chats:user-chats', kwargs={'chat_slug': _chat_slug}))

        if not self.chat_exists(request, message.chat, _chat_slug):
            return redirect(reverse('chats:user-chats', kwargs={'chat_slug': _chat_slug}))

        if not self.can_access_chat(request, message.chat):
            return redirect(self._access_forbidden_url)

        if message.author != request.user:
            return redirect(self._access_forbidden_url)