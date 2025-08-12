from typing import Iterable, List
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from common.models import TimeStampedUUIDModel
from django.contrib.auth import get_user_model


Profile = get_user_model()


class Like(TimeStampedUUIDModel):
    author = models.ForeignKey( 
                                settings.AUTH_USER_MODEL,
                                related_name='given_likes',
                                on_delete=models.CASCADE
                            )
    post = models.ForeignKey( 
                                "posts.Post",
                                related_name='post_likes',
                                on_delete=models.CASCADE
                            )
    
    
    def __str__(self):
        return f"For post: {self.post.slug} given by {self.author.username}"


    class Meta:
        verbose_name = _("Like")
        verbose_name_plural = _("Likes")
        ordering = ['-created_at']

    
    def get_all_likes_authors_list(self) -> List[int]:
        """Returns a list of all users who have liked any post"""
        authors_ids = []
        for like in Like.objects.all():
            if like.author.given_likes is not None:
                authors_ids.append(like.author.id)
                print("Like author", like.author)
        return authors_ids

        
class Dislike(TimeStampedUUIDModel):
    author = models.ForeignKey( 
                                settings.AUTH_USER_MODEL,
                                related_name='given_dislikes',
                                on_delete=models.CASCADE
                            )
    post = models.ForeignKey( 
                                "posts.Post",
                                related_name='post_dislikes',
                                on_delete=models.CASCADE
                            )
    
    
    def __str__(self):
        return f"For post: {self.post.slug} given by {self.author.username}"

    def get_all_dislikes_authors_list(self) -> List[int]:
        """Returns a list of all users who have disliked any post"""
        authors_ids = []
        for dislike in Dislike.objects.all():
            if dislike.author.given_dislikes is not None:
                authors_ids.append(dislike.author.id)
                print("Dislike author", dislike.author)
        return authors_ids

    class Meta:
        verbose_name = _("Dislike")
        verbose_name_plural = _("Dislikes")
        ordering = ['-created_at']
