from django.db import models
from django.conf import settings
from django.core.validators import MaxLengthValidator, validate_slug
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from autoslug import AutoSlugField

from common.models import TimeStampedUUIDModel
from .managers import ActiveCommentsManager


class Comment(TimeStampedUUIDModel):
    objects = models.Manager()
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
                                related_name='comments',
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
    
    class Meta:
        verbose_name = _("Comments")
        verbose_name_plural = _("Comments")
        ordering = ['-created_at']
        
    def __str__(self):
        return self.slug

    def set_slug(self):
        self.slug = f"{self.title}-{self.pkid}"

    def save(self, *args, **kwargs):
        print("Slug", self.slug)
        self.set_slug()
        return super(Comment, self).save(*args, **kwargs)
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
        
        
    def get_absolute_url(self):
        return reverse('posts:post-detail', kwargs={'slug': self.post.slug})
    
    
    