from django.shortcuts import get_object_or_404
from .models import Post

class GetPostObjectMixin():
    def get_object(self):
        _slug = self.kwargs.get('slug', '')
        try:
            post = get_object_or_404(Post, slug=_slug, active=True)
        except Post.DoesNotExist:
            post = None
        print(post)
        return post