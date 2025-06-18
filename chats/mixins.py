from django.shortcuts import get_object_or_404
from .models import Chat, Message


class GetChatObjectMixin():
    def get_object(self):
        slug_ = self.kwargs.get(self.slug_field, '')
        try:
            chat = get_object_or_404(Chat, slug=slug_)
        except Chat.DoesNotExist:
            chat = None
        return chat
    
    
class GetMessageObjectMixin():
    def get_object(self):
        _slug = self.kwargs.get('slug', '')
        try:
            message = get_object_or_404(Message, slug=_slug)
        except Message.DoesNotExist:
            message = None
        return message