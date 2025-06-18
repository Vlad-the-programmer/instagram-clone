from django.contrib import admin
from .models import Comment

class CommentAdmin(admin.ModelAdmin):
    list_display = [  
                    'pkid',  
                    'id', 
                    'author', 
                    'slug',
                    'content',
                    'title',
                    'created_at',
                    'updated_at',
                    'post'
                ]
    list_filter = ("author__username",)
    search_fields = ['pkid', 'post__slug', 'auhtor__username', 'title', 'slug']
    # prepopulated_fields = {'slug': ('title',)}
    
    
admin.site.register(Comment, CommentAdmin)
