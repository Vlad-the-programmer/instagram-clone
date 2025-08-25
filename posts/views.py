from typing import Any, Dict
from django.db import transaction
from django.db.models import QuerySet, Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  UpdateView,
                                  edit)

from comments.forms import CommentCreateForm
from comments.utils import paginate_comments
from users.permissions import PermissionEnum
from .mixins import PostPaginationMixin, PostPermissionMixin
from .models import Post, Tags
from .forms import UpdateForm, CreateForm
from .utils import posts_filter
from . import mixins
from common import mixins as common_mixins

class PostsListView(PostPaginationMixin, ListView):
    """View for displaying a list of published posts with filtering and pagination."""
    model = Post
    queryset = Post.published.select_related('author').prefetch_related('tags')
    template_name = 'index.html'
    context_object_name = 'posts'
    paginate_by = 5
    
    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        if self.request.GET.get('content'):
            queryset, _ = posts_filter(self.request, queryset)
        return queryset
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search_query', '')
        return context
    
class CreatePostView(LoginRequiredMixin,
                     PostPermissionMixin,
                     common_mixins.HandleNotFoundObjectMixin,
                     common_mixins.InvalidFormMixin,
                     CreateView):
    """View for creating a new post."""
    model = Post
    form_class = CreateForm
    template_name = 'posts/post_create.html'
    view_permission_required = (PermissionEnum.ADD_POST,)

    def form_valid(self, form):
        """Handle valid form submission and add success message."""
        response = super().form_valid(form)
        messages.success(self.request, 'Your post has been added!')
        return response

    def get_success_url(self):
        return reverse('posts:post-detail', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Add extra context to the template.
        """
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        return context

class PostDetailView(mixins.GetPostObjectMixin,
                     common_mixins.HandleNotFoundObjectMixin,
                     DetailView):
    """View for displaying a single post with its comments and reactions."""
    model = Post
    template_name = 'posts/post-detail.html'
    context_object_name = 'post'

    def get_queryset(self) -> QuerySet:
        """Optimize the queryset with related data and annotations."""
        return (
            super().get_queryset()
            .select_related('author')
            .prefetch_related('tags')
            .annotate(
                like_count=Count('like', distinct=True),
                dislike_count=Count('dislike', distinct=True),
            )
        )

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add comments, likes, and dislikes to the context."""
        context = super().get_context_data(**kwargs)
        post = self.object
        
        # Optimize queries
        comments = post.comments.select_related('author').all()
        custom_range, page_obj = paginate_comments(self.request, comments, 5)

        # Get like/dislike counts using annotations in the queryset
        like_count = getattr(post, 'like_count', 0)
        dislike_count = getattr(post, 'dislike_count', 0)
        comment_count = getattr(post, 'comment_count', 0)

        context.update({
            'comments': page_obj,
            'custom_range': custom_range,
            'like_count': like_count,
            'dislike_count': dislike_count,
            'comment_form': CommentCreateForm(),
        })
        return context
 
class PostUpdateView(LoginRequiredMixin,
                     PostPermissionMixin,
                     common_mixins.HandleNotFoundObjectMixin,
                     common_mixins.InvalidFormMixin,
                     UpdateView):
    """View for updating an existing post."""
    model = Post
    form_class = UpdateForm
    template_name = 'posts/post_create.html'
    view_permission_required = (PermissionEnum.EDIT_POST,)
    
    def get_queryset(self) -> QuerySet:
        """Limit queryset to posts owned by the current user."""
        return super().get_queryset().filter(author=self.request.user)

    def form_valid(self, form):
        """Handle valid form submission and add success message."""
        response = super().form_valid(form)
        messages.success(self.request, 'Your post has been updated!')
        return response

    def get_success_url(self):
        post = self.get_object()
        return post.get_absolute_url()

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add action context to the template."""
        context = super().get_context_data(**kwargs)
        context['action'] = 'Update'
        return context

class PostDeleteView(LoginRequiredMixin,
                        mixins.PostPermissionMixin,
                        mixins.GetPostObjectMixin,
                        common_mixins.HandleNotFoundObjectMixin,
                        common_mixins.InvalidFormMixin,
                        edit.DeleteView
                    ):
    template_name = 'posts/post_delete.html'
    success_url = reverse_lazy('posts:posts-list')
    view_permission_required = (PermissionEnum.DELETE_POST,)

    def form_valid(self, form):
        """Handle valid form submission and add success message."""
        response = super().form_valid(form)
        messages.success(self.request, 'Post deleted successfully!')
        return response

