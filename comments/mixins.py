from django.contrib.auth.decorators import permission_required

from .models import Comment


class GetCommentObjectMixin():
        
    def get_object(self):
        slug_ = self.kwargs.get('slug', '')
        print("Slug kwarg ", slug_)
        try:
            comment = Comment.active_comments.get(slug=slug_)
        except Comment.DoesNotExist:
            comment = None

        return comment


class CommentPermissionMixin:
    """Mixin to handle comment-related permissions."""
    view_permission_required = None

    def dispatch(self, request, *args, **kwargs):
        if self.view_permission_required:
            return permission_required(
                self.view_permission_required,
                raise_exception=True
            )(super().dispatch)(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)
