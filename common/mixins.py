from typing import Union

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.http.response import HttpResponsePermanentRedirect
from django.urls import reverse
from django.shortcuts import redirect
from django.conf import settings
# Auth
from django.contrib import messages

from chats.models import Message, Chat


class LoginRequiredMixin:
    """Custom authentication mixin that adds messages"""
    def dispatch(self, request, *args, **kwargs):
        print("Request user: ", request.user)
        if not request.user.is_authenticated:
            messages.info(request, "Login first!")
            return redirect(settings.LOGIN_URL)
        return super().dispatch(request, *args, **kwargs)

class BaseChatMessageMixin:
    def chat_exists(self,
                                       request,
                                       chat:Union[Chat, None],
                                       chat_slug: str,
                                       ) -> bool:
        if chat is None:
            messages.error(request, 'Chat does not exist!')
            return False
        return True

    def can_access_chat(self, request, chat:Union[Chat, None]) -> bool:
        if chat.author != request.user or chat.chat_to_user != request.user:
            return False
        return True

class ChatAccessPermissionRequiredMixin(BaseChatMessageMixin):
    def get(self, request, *args, **kwargs):
        chat: Union[Chat, None] = self.get_object()
        _chat_slug = self.kwargs.get(self.slug_field, "")

        if not self.chat_exists(request, chat, _chat_slug):
            return redirect(reverse('chats:user-chats', kwargs={'chat_slug': _chat_slug}))

        if not self.can_access_chat(request, chat):
            raise PermissionDenied


class MessageAccessPermissionRequiredMixin(BaseChatMessageMixin):
    def get(self, request, *args, **kwargs):
        message: Union[Message, None] = self.get_object()
        _chat_slug = self.kwargs.get(self.slug_field, "")

        if message.chat is None:
            messages.error(request, 'Chat does not exist!')
            return redirect(reverse('chats:user-chats', kwargs={'chat_slug': _chat_slug}))

        if message is None:
            messages.error(request, 'Message does not exist!')
            return redirect(reverse('chats:user-chats', kwargs={'chat_slug': _chat_slug}))

        if not self.chat_exists(request, message.chat, _chat_slug):
            return redirect(reverse('chats:user-chats', kwargs={'chat_slug': _chat_slug}))

        if not self.can_access_chat(request, message.chat):
            raise PermissionDenied

        if message.author != request.user:
            raise PermissionDenied