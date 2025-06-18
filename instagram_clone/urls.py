from django.conf import settings
from django.conf.urls.static  import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/',    admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('social-accounts/', include('allauth.socialaccount.urls')),
    path('',          include('posts.urls', namespace='posts')),
    path('users/',    include('users.urls', namespace='users')),
    path('likes/',    include('likes.urls', namespace='likes')),
    path('chats/',    include('chats.urls', namespace='chats')),
    path('comments/', include('comments.urls', namespace='comments')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)