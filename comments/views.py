from typing import Any, Dict, Optional
from django.db import transaction, models
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView

from posts.models import Post
from .models import Comment
from .forms import CommentCreateForm, CommentUpdateForm
from .mixins import GetCommentObjectMixin, CommentPermissionMixin
from .utils import get_comments
from users.permissions import PermissionEnum


class CommentCreateView(LoginRequiredMixin, CommentPermissionMixin, CreateView):
    """
    View for creating a new comment on a post.
    """
    model = Comment
    template_name = 'posts/post-detail.html'
    form_class = CommentCreateForm
    view_permission_required = PermissionEnum.ADD_COMMENT
    
    @transaction.atomic
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handle POST request to create a new comment.
        """
        try:
            post_id = request.POST.get('post_id')
            if not post_id:
                messages.error(request, 'Post ID is required.')
                return redirect('posts:posts-list')
                
            post = get_object_or_404(Post.published, id=post_id)
            form = self.form_class(data=request.POST, files=request.FILES)
            
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = request.user
                comment.post = post
                comment.save()
                
                messages.success(request, 'Your comment has been added!')
                return redirect(comment.get_absolute_url())
                
            # If form is invalid, show errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
                    
            return redirect(post.get_absolute_url())
            
        except Exception as e:
            messages.error(request, 'An error occurred while adding your comment.')
            return redirect('posts:posts-list')
    
    def form_invalid(self, form) -> HttpResponse:
        """Handle invalid form submission."""
        messages.error(
            self.request,
            'Please correct the errors below.'
        )
        return self.render_to_response(self.get_context_data(form=form))
   

class CommentUpdateView(LoginRequiredMixin, CommentPermissionMixin, GetCommentObjectMixin, UpdateView):
    """
    View for updating an existing comment.
    """
    model = Comment
    template_name = 'comments/comment_update.html'
    form_class = CommentUpdateForm
    slug_url_kwarg = 'slug'
    view_permission_required = PermissionEnum.CHANGE_COMMENT
    
    def get_queryset(self) -> QuerySet:
        """Limit queryset to comments owned by the current user."""
        return super().get_queryset().filter(author=self.request.user)
    
    @transaction.atomic
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handle POST request to update a comment.
        """
        comment = self.get_object()
        if comment is None:
            messages.error(request, 'Comment not found.')
            return redirect('posts:posts-list')
            
        form = self.form_class(
            instance=comment,
            data=request.POST,
            files=request.FILES
        )
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Your comment has been updated!')
            return redirect(comment.get_absolute_url())
            
        return self.form_invalid(form)
    
    def form_invalid(self, form) -> HttpResponse:
        """Handle invalid form submission."""
        messages.error(
            self.request,
            'Please correct the errors below.'
        )
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add comment and related data to the template context."""
        context = super().get_context_data(**kwargs)
        context['update_form'] = self.form_class(instance=self.object)
        context['post'] = self.object.post
        context['comments'] = get_comments(self.object.post)
        return context


class CommentDeleteView(LoginRequiredMixin, CommentPermissionMixin, GetCommentObjectMixin, DeleteView):
    """
    View for deleting a comment.
    """
    model = Comment
    template_name = 'comments/comment_delete.html'
    slug_url_kwarg = 'slug'
    view_permission_required = PermissionEnum.DELETE_COMMENT
    
    def get_queryset(self) -> QuerySet:
        """Limit queryset to comments owned by the current user or posts owned by the user."""
        return super().get_queryset().filter(
            models.Q(author=self.request.user) | 
            models.Q(post__author=self.request.user)
        )
    
    @transaction.atomic
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handle POST request to delete a comment.
        """
        comment = self.get_object()
        if comment is None:
            messages.error(request, 'Comment not found.')
            return redirect('posts:posts-list')
            
        post_url = comment.get_absolute_url()
        try:
            comment.delete()
            messages.success(request, 'Your comment has been deleted.')
        except Exception as e:
            messages.error(request, 'An error occurred while deleting the comment.')
            
        return redirect(post_url)
    
    def get_success_url(self) -> str:
        """Return the URL to redirect to after successful deletion."""
        return self.object.get_absolute_url()