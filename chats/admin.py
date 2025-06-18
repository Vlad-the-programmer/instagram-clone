from django.contrib import admin
from .models import Message, Chat


class ChatAdmin(admin.ModelAdmin):
    list_display = (    
                    'id',
                    'author', 
                    'slug', 
                    'chat_to_user', 
                    'created_at',
                    'updated_at'
                )
    list_filter = ("author__username",)
    search_fields = ['post__slug', 'author__username', 'slug']
    prepopulated_fields = {}


class MessageAdmin(admin.ModelAdmin):
    list_display = ( 
                    'pkid',   
                    'id', 
                    'author', 
                    'chat',
                    'message',
                    'sent_for',
                    'status',
                    'created_at',
                    'updated_at'
                )
    list_filter = ("author__username", "sent_for__username")
    search_fields = [ 
                     'pkid',
                     'sent_for__username',
                     'auhtor__username', 
                     'status', 
                     'created_at'
                    ]
    prepopulated_fields = {}

     
admin.site.register(Chat, ChatAdmin)
admin.site.register(Message, MessageAdmin)

