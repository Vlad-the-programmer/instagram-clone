from django.contrib import admin
from .models import Like


class LikeAdmin(admin.ModelAdmin):
    list_display = (    
                    'pkid',
                    'id', 
                    'author', 
                    'post', 
                    'created_at',
                    'updated_at'
                )
    list_filter = ("author__username",)
    search_fields = ['pkid', 'post__slug', 'auhtor__username']
    prepopulated_fields = {}

     
admin.site.register(Like, LikeAdmin)

