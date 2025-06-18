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