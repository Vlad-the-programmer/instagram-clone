from django.db import models
from django.conf import settings
from django.core.validators import MaxLengthValidator, validate_slug
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from autoslug import AutoSlugField

from common.models import TimeStampedUUIDModel


class STATUS(models.TextChoices):
    SENT = "sent", _("Sent")
    UNSENT = "unsent", _("Unsent")
    
    
class Chat(TimeStampedUUIDModel):
    slug = models.SlugField(   
                            unique=True,
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
                            verbose_name=_('Slug'),
                        )
    author = models.ForeignKey( 
                                settings.AUTH_USER_MODEL,
                                related_name='created_chat',
                                on_delete=models.CASCADE
                            )
    chat_to_user = models.ForeignKey(   
                                        settings.AUTH_USER_MODEL,
                                        related_name='foreign_chat',
                                        on_delete=models.CASCADE,
                                        verbose_name=_('User author chat to'),
                                    )
    
    class Meta:
        verbose_name = _("Chat")
        verbose_name_plural = _("Chats")
        ordering = ['-created_at']
        
    def __str__(self):
        return self.slug
        
    def set_slug(self):
        self.slug = slugify(str(self.id) + "-from-" + self.author.username  \
                                     + "-to-" + self.chat_to_user.username )
        
    def get_absolute_url(self):
        return reverse('chats:chat-detail', kwargs={'chat_slug': self.slug})
    
    
class Message(TimeStampedUUIDModel):
    message = models.TextField(
                            max_length=500,
                            blank=True, 
                            null=True,
                            validators=[
                                MaxLengthValidator(
                                    limit_value=100,
                                    message="Message is over 500 letters long!"
                                )
                            ]
                        )
    chat = models.ForeignKey( 
                               Chat,
                                related_name = 'messages',
                                on_delete=models.CASCADE
                            )
    author = models.ForeignKey(
                                settings.AUTH_USER_MODEL,
                                related_name='sent_message',
                                on_delete=models.CASCADE
                            )
    sent_for = models.ForeignKey(  
                                    settings.AUTH_USER_MODEL,
                                    related_name='received_message',
                                    on_delete=models.CASCADE
                                )
    status = models.CharField(  
                                _('Status'),
                                max_length=10,
                                choices=STATUS,
                                default=STATUS.SENT,
                                blank=True, 
                                null=True
                            )
    image = models.ImageField(  
                                null=True, 
                                blank=True, 
                                upload_to=f'messages/'
                            )

    
    class Meta:
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        ordering = ['-created_at']
        
    def __str__(self):
        return self.id + " " + self.author.username
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
        
        
    def get_absolute_url(self):
        return reverse('chats:chat-detail', kwargs={'chat_slug': self.chat.slug})
    
    
    