from typing import Any, Dict
from django.db import transaction, models
from django.db.models import QuerySet, Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, edit

from comments.forms import CommentCreateForm
from comments.utils import paginate_comments
from users.permissions import PermissionEnum
from .mixins import PostPaginationMixin, PostPermissionMixin
from .models import Post, Tags
from .forms import UpdateForm, CreateForm
from .utils import posts_filter
from . import mixins
from common import mixins as common_mixins
from common import utils as common_utils


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
        # Remove the print statement in production
        if __debug__:
            print(context)
        return context
    
    
class CreatePostView(PostPermissionMixin, LoginRequiredMixin, CreateView):
    """View for creating a new post."""
    model = Post
    form_class = CreateForm
    template_name = 'posts/post_create.html'
    view_permission_required = (PermissionEnum.ADD_POST,)
    
    @transaction.atomic
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.form_class(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.author = request.user
                common_utils.set_slug(post, Post.published)
                post.save()
                
                # Add tags in a more efficient way
                tag_titles = form.cleaned_data.get('tags', [])
                tags = Tags.objects.filter(title__in=tag_titles)
                post.tags.set(tags)
                
                messages.success(request, 'Post created successfully!')
                return redirect('posts:post-detail', slug=post.slug)
                
            except Exception as e:
                messages.error(request, f'Error creating post: {str(e)}')
                return redirect('posts:post-create')
                
        messages.error(request, 'Please correct the errors below.')
        return self.form_invalid(form)
    
    def form_invalid(self, form) -> HttpResponse:
        """
        Handle invalid form submission.
        """
        context = self.get_context_data(form=form)
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Add extra context to the template.
        """
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        return context

class PostDetailView(mixins.GetPostObjectMixin, DetailView):
    """View for displaying a single post with its comments and reactions."""
    model = Post
    template_name = 'posts/post-detail.html'
    slug_url_kwarg = 'slug'
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
    
    @method_decorator(permission_required(PermissionEnum.DELETE_POST, raise_exception=True))
    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handle DELETE request to delete a post."""
        post = self.get_object()
        if post is None:
            messages.error(request, 'Post does not exist!')
            return redirect('posts:posts-list')
            
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('posts:posts-list')
 
class PostUpdateView(PostPermissionMixin, LoginRequiredMixin, UpdateView):
    """View for updating an existing post."""
    model = Post
    form_class = UpdateForm
    template_name = 'posts/post_create.html'
    slug_url_kwarg = 'slug'
    view_permission_required = (PermissionEnum.EDIT_POST,)
    
    def get_queryset(self) -> QuerySet:
        """Limit queryset to posts owned by the current user."""
        return super().get_queryset().filter(author=self.request.user)
    
    @transaction.atomic
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handle POST request to update a post."""
        post = self.get_object()
        if post is None:
            messages.error(request, 'Post does not exist!')
            return redirect('posts:posts-list')
        
        form = self.form_class(
            instance=post,
            data=request.POST,
            files=request.FILES
        )
        
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.save()
                
                # Update tags efficiently
                tag_titles = form.cleaned_data.get('tags', [])
                tags = Tags.objects.filter(title__in=tag_titles)
                post.tags.set(tags)
                
                messages.success(request, 'Post updated successfully!')
                return redirect('posts:post-detail', slug=post.slug)
                
            except Exception as e:
                messages.error(request, f'Error updating post: {str(e)}')
                return self.form_invalid(form)
                
        messages.error(request, 'Please correct the errors below.')
        return self.form_invalid(form)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add action context to the template."""
        context = super().get_context_data(**kwargs)
        context['action'] = 'Update'
        return context

class PostDeleteView(LoginRequiredMixin,
                        mixins.PostPermissionMixin,
                        mixins.GetPostObjectMixin,
                        common_mixins.LoginRequiredMixin,
                        edit.DeleteView
                    ):
    template_name = 'posts/post_delete.html'
    success_url = reverse_lazy('posts:posts-list')
    view_permission_required = (PermissionEnum.DELETE_POST,)
    
    def delete(self, request, *args, **kwargs):
        self.request = request
        return super().delete(request, *args, **kwargs)
        
        
    def form_valid(self, form):
        post = self.get_object()
        if post:
            post.delete()
            messages.success(self.request, 'Post deleted!')
            return redirect(self.success_url)
        else:
            messages.error(self.request, 'Post does not exist!')
            
            context={}
            context['post'] = post
            
            return render(self.request, self.template_name, context)


