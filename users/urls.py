from django.urls import path
from allauth.account import views as account

from . import views
from .forms import UserLoginForm
from followers import views as follower_views

app_name='users'

urlpatterns = [
    path('register/', views.register, 
                                            name='register'),
    path('activate/<uidb64>/<token>/', views.activate, 
                                            name='activate'),
    path('login/', account.LoginView.as_view(
                                               form_class=UserLoginForm,
                                            ), name='login'),
    path('logout/', account.LogoutView.as_view(), 
                                            name='logout'),
    path('profile/detail/<uuid:pk>/', views.ProfileDetailView.as_view(),
                                            name='profile-detail'),
    path('profile/delete/<uuid:pk>/', views.ProfileDeleteView.as_view(),
                                            name='profile-delete'),
    path('profile/update/<uuid:pk>/', views.ProfileUpdateView.as_view(),
                                            name='profile-update'),
    
    path('forgot-password/',          views.forgotPassword, 
                                            name='forgotPassword'),
    path('reset-password-validate/<uuid:pk>', views.reset_password_validate,
                                            name='reset-password-validate'),
    path('reset-password/<uuid:pk>',  views.resetPassword, 
                                            name='resetPassword'),
    path('follow/<str:username>',     follower_views.followUser, 
                                            name='follow-user'),
    path('unfollow/<str:username>',   follower_views.unFollowUser, 
                                            name='unfollow-user'),
    path('user-profile/<str:username>', 
                        follower_views.FollowingProfileDetailView.as_view(), 
                                            name='following-user-profile'),
]