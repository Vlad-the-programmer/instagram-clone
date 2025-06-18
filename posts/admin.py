
from django.contrib import admin
from posts.models import Post, Tags


class PostAdmin(admin.ModelAdmin):
    list_display = ( 
                    'pkid',   
                    'id', 
                    'title', 
                    'slug',
                    'active',
                    'author',
                    'status',
                    'created_at',
                    'updated_at'
                )
    list_filter = ("status", 'author__username',)
    search_fields = ['title', 'content', 'tags__title', 'slug', 'status']
    # prepopulated_fields = {'slug': ('title',)}

     
admin.site.register(Post, PostAdmin)
admin.site.register(Tags)

