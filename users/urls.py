from django.urls import path

from . import views
from followers import views as follower_views
from .views import EmailConfirmationSentView

app_name='users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(),
                                            name='register'),
    path('confirm-email-sent/', EmailConfirmationSentView.as_view(),
                                            name='email-confirmation-sent'),
    path('profile/detail/<uuid:pk>/', views.ProfileDetailView.as_view(),
                                            name='profile-detail'),
    path('profile/delete/<uuid:pk>/', views.ProfileDeleteView.as_view(),
                                            name='profile-delete'),
    path('profile/update/<uuid:pk>/', views.ProfileUpdateView.as_view(),
                                            name='profile-update'),
    path('follow/<str:username>',     follower_views.follow_user,
                                            name='follow-user'),
    path('unfollow/<str:username>',   follower_views.unfollow_user,
                                            name='unfollow-user'),
    path('user-profile/<str:username>', 
                        follower_views.FollowingProfileDetailView.as_view(), 
                                            name='following-user-profile'),
]