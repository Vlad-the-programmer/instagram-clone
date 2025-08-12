from typing import Dict, Any

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required

from .models import Post
from .utils import search_posts, posts_filter, paginate_posts


class GetPostObjectMixin():
    def get_object(self):
        _slug = self.kwargs.get('slug', '')
        try:
            post = get_object_or_404(Post, slug=_slug, active=True)
        except Post.DoesNotExist:
            post = None
        print(post)
        return post

class PostPermissionMixin:
    """Mixin to handle post-related permissions."""
    view_permission_required = ()

    @method_decorator(permission_required(view_permission_required, raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PostPaginationMixin:
    """Mixin to handle post pagination and filtering."""
    paginate_by = 5

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        if hasattr(self, 'request') and self.request.GET.get('search_query'):
            queryset, _ = search_posts(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        posts, search_query = posts_filter(self.request, queryset)

        custom_range, page_obj = paginate_posts(
            self.request,
            posts,
            self.paginate_by
        )

        context.update({
            'page_obj': page_obj,
            'custom_range': custom_range,
            'posts': posts,
            'search_query': search_query or self.request.GET.get('search_query', '')
        })
        return context