from django.db import models

class PublishedPostsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)