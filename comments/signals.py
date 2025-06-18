from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

from .models import Comment

@receiver(post_save, sender=Comment)
def save_comment(sender, created, instance, *args, **kwargs):
    comment = instance
    if created:
        comment.save()     