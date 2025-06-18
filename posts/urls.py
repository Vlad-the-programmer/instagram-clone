from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('',                         views.PostsListView.as_view(),
                                                        name='posts-list'),
    path('post/detail/<slug:slug>/', views.PostDetailView.as_view(), 
                                                        name='post-detail'),
    path('post/update/<slug:slug>/', views.PostUpdateView.as_view(), 
                                                        name='post-update'),
    path('post/create/',             views.CreatePostView.as_view(), 
                                                        name='post-create'),
    path('post/delete/<slug:slug>/', views.PostDeleteView.as_view(), 
                                                        name='post-delete'),
    
    
]
