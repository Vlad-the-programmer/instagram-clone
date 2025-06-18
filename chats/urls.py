from django.urls import path
from . import views

app_name = 'chats'

urlpatterns = [
    path('chat/messages/create/<slug:chat_slug>', 
                                            views.MessageCreateView.as_view(),    
                                                    name='messages-create'),
    path('chat/messages/update/<uuid:pk>/', views.MessageUpdateView.as_view(), 
                                                    name='messages-update'),
    path('chat/messages/delete/<uuid:pk>/', views.MessageDeleteView.as_view(),
                                                    name='messages-delete'),
    path('<uuid:user_id>/',       views.ChatListView.as_view(),
                                                    name='user-chats'),
    path('chat/<slug:chat_slug>/detail',    views.ChatDetailView.as_view(),
                                                    name='chat-detail'),
    path('chats/delete/<slug:chat_slug>/',  views.ChatDeleteView.as_view(),
                                                    name='chat-delete'),
    path('chat/create/<uuid:chat_to_user_id>',   views.ChatCreateView.as_view(),    
                                                    name='chat-create'),
]
