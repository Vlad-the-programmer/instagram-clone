from django.db import models

class ActiveCommentsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(disabled=False)