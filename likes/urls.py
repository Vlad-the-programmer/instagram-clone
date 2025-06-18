from django.urls import path
from . import views

app_name = 'likes'

urlpatterns = [
    path('like/create/<slug:post_slug>', views.LikeCreateView.as_view(),    
                                                    name='like-create'),
    path('dislike/create/<slug:post_slug>', views.DislikeCreateView.as_view(),    
                                                    name='dislike-create'),
]
