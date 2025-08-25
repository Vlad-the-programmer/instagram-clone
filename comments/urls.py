from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('comment/create/<slug:post_slug>',          views.CommentCreateView.as_view(),
                                                        name='comment-create'),
    path('comment/update/<slug:slug>/', views.CommentUpdateView.as_view(), 
                                                        name='comment-update'),
    path('comment/delete/<slug:slug>/', views.CommentDeleteView.as_view(), 
                                                        name='comment-delete'),
    
    
]
