from posts.mixins import GetPostObjectMixin


class GetSuccessUrlMixin:
    def get_success_url(self):
        _, _, post = self.get_object()
        return post.get_absolute_url()


class GetLikeOrDislikeMixin:
    def get_object(self):
        post = GetPostObjectMixin.get_object(self)

        obj, created = self.model.objects.get_or_create(
                                                      post=post,
                                                      author=self.request.user
                                                    )
        logger.info(f"{self.model.__name__} given: ", obj)
        return obj, created, post