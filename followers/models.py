from django.contrib.auth import get_user_model
from django.db import models

from common.models import TimeStampedUUIDModel


User = get_user_model()


class UserFollowing(TimeStampedUUIDModel):

    user = models.ForeignKey(    
                                User, 
                                related_name="following", 
                                on_delete=models.CASCADE
                            )
    following_user = models.ForeignKey(  
                                          User, 
                                          related_name="followers",
                                          on_delete=models.CASCADE
                                        )

    class Meta:
        constraints = [
            models.UniqueConstraint(    
                                    fields=['user','following_user'],
                                    name="unique_followers"
                                ),
        ]

        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} follows {self.following_user.username}"
        
        
    def has_chat_to_user_perms(self, request, user_to_chat_id):
        if request.user.is_authenticated \
                            and self.following_user == user_to_chat_id:
            return True
        return False
    
    
