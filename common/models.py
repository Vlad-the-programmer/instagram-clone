import uuid
from datetime import timezone

from django.db import models


class TimeStampedUUIDModel(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    deleted_at = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        """
        Override the default delete method to perform a soft delete.
        Sets is_active to False instead of actually deleting the record.
        """
        using = kwargs.get('using', 'default')

        # Don't do anything if already soft-deleted
        if not self.is_active:
            return

        # Update the is_active flag
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=['is_active', 'updated_at'])

        # Call any post-save signals if needed
        models.signals.pre_delete.send(
            sender=self.__class__,
            instance=self,
            using=using,
            soft_delete=True  # Custom flag to indicate soft delete
        )
