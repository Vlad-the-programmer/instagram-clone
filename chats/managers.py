from django.db import models

class ActiveChatsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class ActiveMessagesManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)