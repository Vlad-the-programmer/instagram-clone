from typing import Any, Dict
from django.db import models
from django.db.models import QuerySet
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView

from .models import Comment
from .forms import CommentCreateForm, CommentUpdateForm
from .mixins import (GetCommentObjectMixin,
                     CommentPermissionMixin,
                     )
from .utils import get_comments
from users.permissions import PermissionEnum
from common import mixins as common_mixins
from posts.mixins import GetPostObjectMixin


class CommentCreateView(LoginRequiredMixin,
                        CommentPermissionMixin,
                        common_mixins.HandleNotFoundObjectMixin,
                        common_mixins.InvalidFormMixin,
                        CreateView):
    """
    View for creating a new comment on a post.
    """
    model = Comment
    template_name = 'posts/post-detail.html'
    form_class = CommentCreateForm
    view_permission_required = PermissionEnum.ADD_COMMENT

    def get_object(self):
        """Get post object by slug or post_slug if we want to get a post for a comment."""
        return GetPostObjectMixin.get_object(self, post_slug = self.kwargs.get('post_slug'))

    def form_valid(self, form):
        """Handle valid form submission and add success message."""
        response = super().form_valid(form)
        messages.success(self.request, 'Your comment has been added!')
        return response

    def get_success_url(self):
        comment = self.get_object()
        return comment.get_absolute_url()

class CommentUpdateView(LoginRequiredMixin,
                        CommentPermissionMixin,
                        GetCommentObjectMixin,
                        common_mixins.HandleNotFoundObjectMixin,
                        common_mixins.InvalidFormMixin,
                        UpdateView):
    """
    View for updating an existing comment.
    """
    model = Comment
    template_name = 'comments/comment_update.html'
    form_class = CommentUpdateForm
    view_permission_required = PermissionEnum.CHANGE_COMMENT
    
    def get_queryset(self) -> QuerySet:
        """Limit queryset to comments owned by the current user."""
        return super().get_queryset().filter(author=self.request.user)

    def form_valid(self, form):
        """Handle valid form submission and add success message."""
        response = super().form_valid(form)
        messages.success(self.request, 'Your comment has been updated!')
        return response

    def get_success_url(self):
        comment = self.get_object()
        return comment.get_absolute_url()

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add comment and related data to the template context."""
        context = super().get_context_data(**kwargs)
        context['update_form'] = self.form_class(instance=self.object)
        context['post'] = self.object.post
        context['comments'] = get_comments(self.object.post)
        return context

class CommentDeleteView(LoginRequiredMixin,
                        CommentPermissionMixin,
                        GetCommentObjectMixin,
                        common_mixins.HandleNotFoundObjectMixin,
                        common_mixins.InvalidFormMixin,
                        DeleteView):
    """
    View for deleting a comment.
    """
    model = Comment
    template_name = 'comments/comment_delete.html'
    view_permission_required = PermissionEnum.DELETE_COMMENT
    
    def get_queryset(self) -> QuerySet:
        """Limit queryset to comments owned by the current user or posts owned by the user."""
        return super().get_queryset().filter(
            models.Q(author=self.request.user) | 
            models.Q(post__author=self.request.user)
        )

    def form_valid(self, form):
        """Handle valid form submission and add success message."""
        response = super().form_valid(form)
        messages.success(self.request, 'Your comment has been deleted!')
        return response

    def get_success_url(self):
        comment = self.get_object()
        return comment.get_absolute_url()

