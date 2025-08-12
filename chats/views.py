import logging
from typing import Dict, Any, Optional, Tuple
from django.db import transaction
from django.db.models import Q, QuerySet, Count
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, Http404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, edit
from rest_framework.reverse import reverse_lazy

from . import mixins
from .forms import MessageCreateUpdateForm
from .models import Chat, Message, STATUS
from .mixins import (GetChatObjectMixin,
                     ChatAccessPermissionRequiredMixin,
                     GetMessageObjectMixin,
                     MessageAccessPermissionRequiredMixin)
from common.mixins import LoginRequiredMixin as CommonLoginRequiredMixin

logger = logging.getLogger(__name__)
Profile = get_user_model()


class ChatListView(CommonLoginRequiredMixin, ListView):
    """
    View for listing all active chats of the current user.
    Orders chats by most recently updated and includes unread message counts.
    """
    model = Chat
    template_name = 'chats/chats-list.html'
    context_object_name = 'chats'
    
    def get_queryset(self) -> QuerySet:
        """
        Get the list of chats for the current user with optimized queries.
        """
        current_user = self.request.user
        queryset = (
            self.model.active_chats
            .filter(Q(author=current_user) | Q(chat_to_user=current_user))
            .select_related('author', 'chat_to_user')
            .prefetch_related('messages')
            .order_by('-updated_at')
        )
        logger.debug("Fetched %d chats for user %s", queryset.count(), current_user.username)
        return queryset
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add unread messages count to the context."""
        context = super().get_context_data(**kwargs)
        context['unread_counts'] = {
            chat.id: chat.messages.filter(status=STATUS.UNREAD, author__isnull=False)
                                 .exclude(author=self.request.user)
                                 .count()
            for chat in context['chats']
        }
        return context
    
    
class ChatDetailView(CommonLoginRequiredMixin, GetChatObjectMixin, 
                      ChatAccessPermissionRequiredMixin, DetailView):
    """
    View for displaying a chat conversation between two users.
    Handles displaying messages and marking them as read.
    """
    model = Chat
    template_name = 'chats/chat-detail.html'
    context_object_name = 'chat'
    slug_field = 'chat_slug'
    slug_url_kwarg = 'chat_slug'
    paginate_by = 50
    
    def get_queryset(self) -> QuerySet:
        """Optimize the queryset with related data."""
        return (
            super().get_queryset()
            .select_related('author', 'chat_to_user')
            .prefetch_related('messages__author')
        )

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Add messages to the context and mark unread messages as read.
        """
        context = super().get_context_data(**kwargs)
        chat = self.get_object()
        current_user = self.request.user
        
        # Mark messages as read in a single query
        if chat:
            unread_messages = chat.messages.filter(
                status=STATUS.UNREAD,
                author__isnull=False
            ).exclude(author=current_user)
            
            if unread_messages.exists():
                unread_messages.update(status=STATUS.READ)
        
        # Get messages with optimized query
        messages = chat.messages.select_related('author').order_by('-created_at')
        
        # Determine the other user in the chat
        receiver = chat.chat_to_user if current_user == chat.author else chat.author
        logger.debug(f"Reciever: {receiver}")

        context.update({
            "receiver": receiver,
            "initial_messages": messages[:self.paginate_by],
            "has_more": messages.count() > self.paginate_by,
            "form": MessageCreateUpdateForm(),
            "user": current_user,
            "chat_slug": chat.slug
        })
        
        return context
        

class ChatCreateView(CommonLoginRequiredMixin, CreateView):
    """
    View for creating a new chat or retrieving an existing one between two users.
    Ensures thread safety and prevents duplicate chats.
    """
    template_name = 'chats/chat-detail.html'
    model = Chat

    def get_chat(self, user1: Profile, user2: Profile) -> Optional[Chat]:
        return  (
                Chat.active_chats
                .select_for_update()
                .filter(
                    (Q(author=user1, chat_to_user=user2) |
                     Q(author=user2, chat_to_user=user1))
                )
                .first()
            )

    def get_or_create_chat(self, user1: Profile, user2: Profile) -> Tuple[Chat, bool]:
        """
        Thread-safe method to get or create a chat between two users.
        Uses select_for_update to prevent race conditions.
        """
        with transaction.atomic():
            # Try to find an existing chat in either direction
            chat = self.get_chat(user1, user2)
            
            if chat:
                return chat, False
                
            # Create new chat if none exists
            chat = Chat.objects.create(
                author=user1,
                chat_to_user=user2,
            )
            logger.info(
                "Created new chat between %s and %s",
                user1.username,
                user2.username
            )
            return chat, True
    
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handle POST request to create or get a chat."""
        try:
            chat_to_user_id = self.kwargs.get('chat_to_user_id')
            if not chat_to_user_id:
                raise Http404("User ID not provided")
                
            chat_to_user = get_object_or_404(Profile, id=chat_to_user_id)
            
            if chat_to_user == request.user:
                messages.error(request, "You cannot start a chat with yourself!")
                return redirect(reverse_lazy("chats:user-chats", kwargs={"user_id": request.user.id}))
            
            # Get or create chat in a thread-safe way
            chat, created = self.get_or_create_chat(request.user, chat_to_user)
            
            if not chat.is_active:
                messages.error(request, "This chat has been deleted.")
                return redirect(reverse_lazy("chats:user-chats", kwargs={"user_id": request.user.id}))
                
            if created:
                messages.success(request, f"Started a new chat with {chat_to_user.username}")
            else:
                messages.info(request, f"You already have a chat with {chat_to_user.username}")
                
            return redirect(chat.get_absolute_url())
            
        except Exception as e:
            logger.error("Error creating/retrieving chat: %s", str(e), exc_info=True)
            messages.error(request, "An error occurred while creating the chat.")
            return redirect(reverse_lazy("chats:user-chats", kwargs={"user_id": request.user.id}))
    
    def get_success_url(self) -> str:
        """Get the URL to redirect to after successful creation."""
        chat_to_user_id = self.kwargs.get('chat_to_user_id')
        chat = self.get_chat(self.request.user, get_object_or_404(Profile, id=chat_to_user_id))
        if chat:
            return chat.get_absolute_url()
        return reverse_lazy("chats:user-chats")

class ChatDeleteView(CommonLoginRequiredMixin, GetChatObjectMixin,
                      ChatAccessPermissionRequiredMixin, DeleteView):
    """
    View for soft-deleting a chat.
    Implements proper permission checks and transaction safety.
    """
    model = Chat
    context_object_name = 'chat'
    template_name = 'chats/chats-list.html'
    slug_field = 'chat_slug'
    slug_url_kwarg = 'chat_slug'

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handle DELETE request with transaction safety.
        """
        try:
            with transaction.atomic():
                chat = self.get_object()
                if not chat:
                    messages.error(request, "Chat not found.")
                    return redirect(self.get_success_url())
                
                # Soft delete the chat
                chat.is_active = False
                chat.save(update_fields=['is_active', 'updated_at'])
                
                logger.info(
                    "Chat %s was deleted by %s",
                    chat.chat_slug,
                    request.user.username
                )
                
                messages.success(request, "Chat has been deleted.")
                return redirect(self.get_success_url())
                
        except Exception as e:
            logger.error("Error deleting chat: %s", str(e), exc_info=True)
            messages.error(request, "An error occurred while deleting the chat.")
            return redirect(self.get_success_url())
    
    def get_success_url(self) -> str:
        """Return URL to redirect to after successful deletion."""
        return reverse('chats:user-chats', kwargs={'user_id': self.request.user.id})
        
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add active chats to the context."""
        context = super().get_context_data(**kwargs)
        context['chats'] = (
            Chat.active_chats
            .filter(Q(author=self.request.user) | Q(chat_to_user=self.request.user))
            .select_related('author', 'chat_to_user')
            .order_by('-updated_at')
        )
        return context    
    
    
# class MessageCreateView(common_mixins.LoginRequiredMixin,

class MessageUpdateView(CommonLoginRequiredMixin,
                        mixins.GetMessageObjectMixin,
                        mixins.MessageAccessPermissionRequiredMixin,
                        edit.UpdateView
                        ):
    template_name = 'chats/chat-detail.html'
    context_object_name = 'message'
    form_class = MessageCreateUpdateForm
    slug_field = 'chat_slug'

    def post(self, request, *args, **kwargs):
        _chat_slug = self.kwargs.get('chat_slug', '')
        message = self.get_object()

        if message is None:
            messages.error(request, 'Message does not exist!')
            return redirect(reverse('chats:chat-detail', kwargs={'chat_slug': _chat_slug}))

        print(request.POST)
        form = MessageCreateUpdateForm(
                                        instance=message,
                                        data=request.POST,
                                        files=request.FILES
                                    )
            
        if form.is_valid():
            message = form.save(commit=False)
            
            message.author = request.user
            message.save()
                
            messages.success(request, 'Updated!')    
            return redirect(message.chat.get_absolute_url())
        
        messages.error(request, 'Invalid data!')    
        return redirect(message.chat.get_absolute_url())

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        message = self.get_object()
        context['form'] = MessageCreateUpdateForm(instance=message)
        context['chat'] = context['message'].chat
        return context
        
    
    def get_success_url(self, *args, **kwargs):
        print(kwargs)
        context = self.get_context_data(**kwargs)
        message = context['message']
        return message.chat.get_absolute_url()

class MessageDeleteView(CommonLoginRequiredMixin,
                        mixins.GetMessageObjectMixin,
                        mixins.MessageAccessPermissionRequiredMixin,
                        edit.DeleteView
                        ):
    model = Message
    context_object_name = 'message'
    template_name = 'chats/chat-detail.html'
    slug_field = 'chat_slug'
    
    def delete(self, request, *args, **kwargs):
        self.request = request
        _chat_slug = self.kwargs.get('chat_slug', '')
        message = self.get_object()
        
        if message is None:
            messages.error(request, 'Message does not exist!')    
            return redirect(reverse('chats:chat-detail', kwargs={'chat_slug': _chat_slug}))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat'] = context['message'].chat
        return context
    
    
    def get_success_url(self, *args, **kwargs):
        message = self.get_object()
        return reverse(message.chat.get_absolute_url())
    