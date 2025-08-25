import logging
from typing import Optional, Dict, Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpRequest
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.views.generic import DetailView
from django.db.models import QuerySet

from .models import UserFollowing
from common.decorators import login_required

logger = logging.getLogger(__name__)

Profile = get_user_model()


def get_redirect_url(username: str) -> str:
    """Generate redirect URL for user profile."""
    return reverse("users:following-user-profile", kwargs={'username': username})


@login_required
def follow_user(request: HttpRequest, username: str) -> HttpResponse:
    """
    View to follow a user.
    
    Args:
        request: The HTTP request object
        username: Username of the user to follow
        
    Returns:
        HttpResponse: Redirects to the user's profile
    """
    user_to_follow = get_object_or_404(Profile, username=username)
    current_user = request.user
    redirect_url = get_redirect_url(user_to_follow.username)

    # Check if trying to follow self
    if user_to_follow == current_user:
        messages.warning(request, "You cannot follow yourself!")
        return redirect(redirect_url)
    
    # Check if already following
    if current_user.is_following(user_to_follow.username):
        messages.info(request, f"You are already following {user_to_follow.username}!")
        return redirect(redirect_url)
    
    # Create the follow relationship
    try:
        with transaction.atomic():
            UserFollowing.objects.create(
                user=current_user,
                following_user=user_to_follow
            )
        messages.success(request, f"You are now following {user_to_follow.username}!")
        logger.info(f"User {current_user.username} started following {user_to_follow.username}")
    except Exception as e:
        logger.error(f"Error following user: {e}", exc_info=True)
        messages.error(request, "An error occurred while trying to follow the user.")
    
    return redirect(redirect_url)


@login_required
def unfollow_user(request: HttpRequest, username: str) -> HttpResponse:
    """
    View to unfollow a user.
    
    Args:
        request: The HTTP request object
        username: Username of the user to unfollow
        
    Returns:
        HttpResponse: Redirects to the user's profile
    """
    user_to_unfollow = get_object_or_404(Profile, username=username)
    current_user = request.user
    redirect_url = get_redirect_url(user_to_unfollow.username)

    # Check if trying to unfollow self
    if user_to_unfollow == current_user:
        messages.warning(request, "You cannot unfollow yourself!")
        return redirect(redirect_url)
    
    # Check if not following
    if not current_user.is_following(user_to_unfollow.username):
        messages.info(request, f"You are not following {user_to_unfollow.username}!")
        return redirect(redirect_url)
    
    # Remove the follow relationship
    try:
        with transaction.atomic():
            following = UserFollowing.objects.get(
                user=current_user,
                following_user=user_to_unfollow
            )
            following.delete()
        messages.success(request, f"You have unfollowed {user_to_unfollow.username}.")
        logger.info(f"User {current_user.username} unfollowed {user_to_unfollow.username}")
    except UserFollowing.DoesNotExist:
        messages.info(request, f"You are not following {user_to_unfollow.username}.")
    except Exception as e:
        logger.error(f"Error unfollowing user: {e}", exc_info=True)
        messages.error(request, "An error occurred while trying to unfollow the user.")
    
    return redirect(redirect_url)


class FollowingProfileDetailView(LoginRequiredMixin, DetailView):
    """
    View to display a user's profile with follow/unfollow functionality.
    """
    model = Profile
    template_name = "followers/followerProfile_detail.html"
    context_object_name = 'profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_object(self, queryset: Optional[QuerySet] = None) -> Profile:
        """
        Get the profile object or return 404 if not found.
        """
        username = self.kwargs.get(self.slug_url_kwarg)
        if not username:
            raise Http404("No username provided")
            
        try:
            return Profile.objects.select_related('user').get(username=username)
        except Profile.DoesNotExist as e:
            logger.warning(f"Profile not found: {username}")
            raise Http404("User not found") from e
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Add additional context to the template.
        """
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        current_user = self.request.user
        
        context.update({
            'is_following': current_user.is_following(profile.username),
            'can_follow': current_user != profile,
            'followers_count': profile.followers.count(),
            'following_count': profile.following.count(),
        })
        
        return context
    