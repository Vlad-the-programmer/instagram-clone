import logging
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, get_object_or_404
# Auth
from django.contrib.auth import get_user_model
from django.contrib import messages
# Generic class-based views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import detail, edit, list

from .forms import MessageCreateUpdateForm, CreateChatForm
from .models import Chat, Message
from . import mixins
from common import mixins as common_mixins


logger = logging.getLogger(__name__)

Profile = get_user_model()


class ChatListView(LoginRequiredMixin,
                   common_mixins.LoginRequiredMixin,
                   list.ListView
                ):
    model = Chat
    template_name = 'chats/chats-list.html'
    context_object_name = 'chats'
        
        
    def get(self, request, *args, **kwargs):
        self.request = request
        return super().get(request, *args, **kwargs)
    
    
    def get_queryset(self):
        return Chat.objects.filter(author=self.request.user)
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    
class ChatDetailView(   
                        LoginRequiredMixin,
                        mixins.GetChatObjectMixin,
                        common_mixins.LoginRequiredMixin,
                        detail.DetailView
                    ):
    model = Chat
    template_name = 'chats/chat-detail.html'
    context_object_name = 'chat'
    slug_field = 'chat_slug'
    
    
    def get(self, request, *args, **kwargs):
        self.request = request
        
        chat = self.get_object()
        if chat is None:
            messages.error(request, 'Chat does not exist!')    
            return redirect(chat.get_absolute_url())
        return super().get(request, *args, **kwargs)
    
        
    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(**kwargs)
        # context["_"] = None
        return context
        

class ChatCreateView(LoginRequiredMixin, 
                     common_mixins.LoginRequiredMixin,
                     edit.CreateView):
    template_name = 'chats/chat-detail.html'
    form_class=CreateChatForm
    context_object_name = 'chat'
    
    def get_object(self):
        chat_to_user_id = self.kwargs.get('chat_to_user_id', '')
        chat, created = Chat.objects.get_or_create(chat_to_user__id=chat_to_user_id)
        return chat, created
    
    def post(self, request, *args, **kwargs):
        self.request = request
        
        chat_to_user_id = self.kwargs.get('chat_to_user_id', '')
        chat, created = self.get_object()
        print("Chat id  ", chat.id)
        
        if created:
            chat.set_slug()
            chat.author = self.request.user
            chat.chat_to_user = Profile.objects.get(id=chat_to_user_id)
            chat.save()
            logging.info(f"Chat with {chat.chat_to_user.get_username()} \
                was created by {chat.author.get_username()}")
            
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        chat, _ = self.get_object()
        return chat.get_absolute_url()
    
    # # Chat chat_to_user_id ??
    def form_valid(self, form):
        return redirect(self.get_success_url())
      
      
class ChatDeleteView(   
                        LoginRequiredMixin, 
                        mixins.GetChatObjectMixin,
                        common_mixins.LoginRequiredMixin,
                        edit.DeleteView
                    ):
    model = Chat
    context_object_name = 'chat'
    template_name = 'chats/chats-list.html'
    

    def delete(self, request, *args, **kwargs):
        self.request = request
        
        chat = self.get_object()
        if chat is None:
            messages.error(request, 'Chat does not exist!')    
            return redirect(chat.get_absolute_url())
        return super().delete(request, *args, **kwargs)
    
    
    def get_success_url(self):
        return reverse('chats:user-chats', kwargs={
                                            'user_id': self.request.user.id
                                            }
                        )
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chats'] = Chat.objects.filter(author=self.request.user)
        return context    
    
    
class MessageCreateView(LoginRequiredMixin,
                        common_mixins.LoginRequiredMixin,
                        edit.CreateView):
    template_name = 'chats/chat-detail.html'
    model = Message
    context_object_name = 'message'
    form_class = MessageCreateUpdateForm
    
    
    def post(self, request, *args, **kwargs):
        messages.success(request, 'Created!')
        return super().post(request, *args, **kwargs)
    
 
    def form_valid(self, form):
        chat_slug = self.kwargs.get('chat_slug', '')
        author = self.request.user
        chat = Chat.objects.filter(slug=chat_slug, author=author)
        
        message = form.save(commit=False)
        message.author = author
        message.chat = chat
        message.sent_for = chat.chat_to_user
        message.save()
        return redirect(chat.get_absolute_url())
    
    # def get_success_url(self, *args, **kwargs):
    #     print(kwargs)
    #     context = self.get_context_data(**kwargs)
    #     message = context['message']
    #     return message.chat.get_absolute_url()
        
        
class MessageUpdateView(    
                            LoginRequiredMixin,
                            mixins.GetMessageObjectMixin,
                            common_mixins.LoginRequiredMixin,
                            edit.UpdateView
                        ):
    template_name = 'chats/chat-detail.html'
    context_object_name = 'message'
    form_class = MessageCreateUpdateForm
    
    
    def post(self, request, slug, *args, **kwargs):
        message = self.get_object()
        
        if message is None:
            messages.error(request, 'Message does not exist!')    
            return redirect(message.chat.get_absolute_url())
        
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
        

class MessageDeleteView(    
                            LoginRequiredMixin,
                            mixins.GetMessageObjectMixin, 
                            common_mixins.LoginRequiredMixin,
                            edit.DeleteView
                        ):
    model = Message
    context_object_name = 'message'
    template_name = 'chats/chat-detail.html'
    
    
    def delete(self, request, *args, **kwargs):
        self.request = request
        
        message = self.get_object()
        
        if message is None:
            messages.error(request, 'Message does not exist!')    
            return redirect(message.chat.get_absolute_url())
        return super().delete(request, *args, **kwargs)
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat'] = context['message'].chat
        return context
    
    
    def get_success_url(self, *args, **kwargs):
        message = self.get_object()
        return reverse(message.chat.get_absolute_url())
            
    
    
    