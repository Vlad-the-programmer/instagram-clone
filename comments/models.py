from django.db import models
from django.conf import settings
from django.core.validators import MaxLengthValidator, validate_slug
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from autoslug import AutoSlugField

from common.models import TimeStampedUUIDModel
from .managers import ActiveCommentsManager
from common import utils as custom_utils


class Comment(TimeStampedUUIDModel):
    active_comments = ActiveCommentsManager()
    
    content = models.TextField( 
                                verbose_name=_('Comment content'),
                                max_length=500,
                                blank=True, 
                                null=True,
                                validators=[
                                    MaxLengthValidator(
                                        limit_value=100,
                                        message="Comment is over 500 letters long!"
                                        )
                                    ]
                                )
    slug = AutoSlugField(   
                            populate_from='title', 
                            unique=True,
                            unique_with=['title'],
                            always_update=True,
                            max_length=100,
                            blank=True,
                            null=True,
                            validators=[
                                validate_slug, 
                                MaxLengthValidator(
                                    limit_value=100,
                                    message="Slug is over 100 letters long!"
                                    )
                                ],
                        )
    author = models.ForeignKey( 
                                settings.AUTH_USER_MODEL,
                                related_name='comments',
                                on_delete=models.CASCADE
                            )
    post = models.ForeignKey(   
                                'posts.Post',
                                related_name='comment',
                                on_delete=models.CASCADE
                            )
    title = models.CharField(   
                             verbose_name=_('Comment title'),
                             max_length=500,
                             blank=True, 
                             null=True,
                             validators=[
                                  MaxLengthValidator(
                                    limit_value=100,
                                    message="Title is over 100 letters long!"
                                    )
                                ]
                            )
    image = models.ImageField(  
                                verbose_name=_('Comment image'),
                                null=True, 
                                blank=True, 
                                upload_to=f'comments/{slug}'
                            )
    disabled = models.BooleanField(default=False, blank=True, null=True)
    
    
    class Meta:
        verbose_name = _("Comments")
        verbose_name_plural = _("Comments")
        ordering = ['-created_at']
        
    def __str__(self):
        return self.slug
    
    def save(self, *args, **kwargs):
        print("Slug", self.slug)
        # existingComment = Comment.active_comments.filter(slug=self.slug)
        
        # if existingComment.exists():
        #     self.slug = slugify(self.title + "-" + self.pkid) 
        custom_utils.set_slug(self, Comment)
        return  super(Comment, self).save(*args, **kwargs)
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
        
        
    def get_absolute_url(self):
        return reverse('posts:post-detail', kwargs={'slug': self.post.slug})
    
    
    