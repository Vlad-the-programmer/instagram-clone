import uuid
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_slug, MaxLengthValidator
from autoslug import AutoSlugField

from common.models import TimeStampedUUIDModel
from .managers import PublishedPostsManager
from common import utils as common_utils


class STATUS(models.TextChoices):
    DRAFT = "draft", _("Draft")
    PUBLISH = "publish", _("Publish")
    

class Post(TimeStampedUUIDModel):
    objects = models.Manager()
    published = PublishedPostsManager()
    
    title = models.CharField(   
                             verbose_name=_('Title'),
                             max_length=100,
                             validators=[
                                  MaxLengthValidator(
                                    limit_value=100,
                                    message="Slug is over 100 letters long!"
                                    )
                                ]
                             )
    content = models.TextField( 
                                verbose_name=_('Post content'), 
                                null=True, 
                                blank=True
                            )
    active = models.BooleanField(
                                    verbose_name=_('Active'), 
                                    default=True
                                )
    slug = AutoSlugField(   
                            populate_from='title', 
                            unique=True,
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
                                ]
                        )
    tags = models.ManyToManyField('Tags', blank=True)
    author = models.ForeignKey( 
                                settings.AUTH_USER_MODEL,
                                related_name='profile',
                                on_delete=models.CASCADE
                            )
    likes = models.ForeignKey( 
                                "likes.Like",
                                related_name='likes',
                                on_delete=models.CASCADE,
                                blank=True, 
                                null=True
                            )
    # category = models.ForeignKey('category.Category',
    #                              on_delete=models.CASCADE,
    #                              blank=True,
    #                              null=True)
    status = models.CharField(  
                                verbose_name=_('Post Status'), 
                                max_length=10,
                                choices=STATUS, 
                                default=STATUS.DRAFT,
                                blank=True, 
                                null=True
                            )
  
    image = models.ImageField(  
                                verbose_name=_('Post image'),
                                null=True, 
                                blank=True, 
                                default="default.jpg", 
                                upload_to='posts'
                            )
    
    def __str__(self):
        return self.title


    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug', 'active', 'title'])
        ]

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
        
    def save(
        self,
        force_insert = ...,
        force_update = ...,
        using = ...,
        update_fields = ...,
        **kwargs
    ):
        """Save an instance including **kwargs which an author, tags"""
        self.author = self.kwargs.get("author")
        common_utils.set_slug(self, self.__class__.published)

        # Add tags in a more efficient way
        tag_titles = self.kwargs.get("tags", [])
        tags = Tags.objects.filter(title__in=tag_titles)
        self.tags.set(tags)

        return super().save(force_insert, force_update, using, update_fields)

    def get_absolute_url(self):
        return reverse('posts:post-detail', kwargs={'slug': self.slug})
        
        
class Tags(TimeStampedUUIDModel):
    title = models.CharField(   
                             max_length=200,
                             validators=[
                              MaxLengthValidator(
                                    limit_value=200,
                                    message="Slug is over 100 letters long!"
                                    )
                                ]
                             )
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title'])
        ]
