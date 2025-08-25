from django.db import models
from django.shortcuts import get_object_or_404
from django.core import validators
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField

import uuid

from .managers import UserManager
from .permissions import (PermissionEnum,
                          PermissionDescriptionEnum,
                          CustomPermissionEnum)


class GenderChoices(models.TextChoices):
    MALE = "M", _("Male")
    FEMALE = "F", _("Female")
    OTHER = "O", _("Other")
    PREFER_NOT_TO_SAY = "prefer_not_to_say", _("Prefer not to say")


class Profile(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]
    
    objects = UserManager()

    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField( 
                              verbose_name=_("Email"), 
                              unique=True, 
                              blank=True,
                              null=True, 
                              max_length=254,
                              validators=[
                                            validators.EmailValidator()
                                        ])
    first_name = models.CharField(  
                                  verbose_name=_("First Name"),
                                  max_length=100, 
                                  blank=True, 
                                  null=True
                                )
    last_name = models.CharField(   
                                 verbose_name=_("Last Name"),
                                 max_length=100, 
                                 blank=True, 
                                 null=True
                                )
    gender = models.CharField(
                                verbose_name=_('Gender'),
                                max_length=40,
                                choices=GenderChoices,
                                default=_('Male'),
                                null=True)
    country = CountryField(
                            blank_label=_('(select country)'),
                            default='',
                            max_length=50,
                        )
    password = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(    
                                    verbose_name=_("Username"),
                                    unique=True, 
                                    max_length=100, 
                                    blank=True, 
                                    null=True
                                )
    featured_img = models.ImageField(
                                        verbose_name=_('A profile image'),
                                        upload_to=f'profiles/', 
                                        default='profiles/profile_default.jpg'
                                    )
    date_joined = models.DateTimeField(auto_now_add=True, null=True)
    last_login = models.DateTimeField(
                                        _('Last logged in'),
                                        null=True, 
                                        blank=True
                                    )
    is_staff = models.BooleanField(default=False, blank=True, null=True)
    is_active = models.BooleanField(default=False, blank=True, null=True)
    is_superuser = models.BooleanField(default=False, blank=True, null=True)
    
    
    def __str__(self):
        return f"{self.username} has email {self.email}"
        
    def set_username(self):
        return self.email.split('@')[0].lower()

    def has_perm(self, perm, obj=None):
        # Superusers have all permissions
        if self.is_superuser:
            return True

        # Check for specific permissions
        return super().has_perm(perm, obj)

    def has_add_permission(self, obj=None):
        """Check if user can add objects"""
        return self.is_active  # All active users can add

    def has_change_permission(self, obj=None):
        """Check if user can change objects"""
        if obj is None:
            return self.is_active
        return self.is_active and (self == obj.user or self.is_staff)

    def has_delete_permission(self, obj=None):
        """Check if user can delete objects"""
        if obj is None:
            return self.is_staff  # Only staff can delete in general
        return self.is_staff or (self == obj.user)

    def has_follow_permission(self, obj=None):
        """Check if user can follow others"""
        return self.is_active

    def has_unfollow_permission(self, obj=None):
        """Check if user can unfollow others"""
        return self.is_active

    def has_module_perms(self, app_label):
        # Superusers have access to all modules
        if self.is_superuser:
            return True

        # Regular users have access to all modules
        return True
    
    def get_user_perms(self) -> dict[str, bool]:
        return {
                    PermissionEnum.ADD_POST:   self.has_add_permission(),
                    PermissionEnum.EDIT_POST: self.has_change_permission(),
                    PermissionEnum.DELETE_POST: self.has_delete_permission(),
                    PermissionEnum.FOLLOW_USER: self.has_follow_permission(),
                    PermissionEnum.UNFOLLOW_USER: self.has_follow_permission(),
                    PermissionEnum.CHANGE_PROFILE: self.has_change_permission(),
                    PermissionEnum.DELETE_PROFILE: self.has_delete_permission(),
                    PermissionEnum.ADD_COMMENT: self.has_add_permission(),
                    PermissionEnum.CHANGE_COMMENT: self.has_change_permission(),
                    PermissionEnum.DELETE_COMMENT: self.has_delete_permission(),
                    PermissionEnum.ADD_LIKE: self.has_add_permission(),
                    PermissionEnum.DELETE_LIKE: self.has_delete_permission(),
                    PermissionEnum.ADD_DISLIKE: self.has_add_permission(),
                    PermissionEnum.DELETE_DISLIKE: self.has_delete_permission(),
                    CustomPermissionEnum.CHAT:   self.has_add_permission()
                }
        
    @classmethod
    def get_user_by_email(cls, email):
        try:
            user = get_object_or_404(cls.__class__, email__exact=email)
        except:
            user = None
            
        if user is not None:
            return True
        return False  
    
    @property
    def get_full_name(self):
        return f"{self.first_name.title()} {self.last_name.title()}"
    
    @property
    def get_short_name(self):
        return self.username.title()
        
    @property
    def imageURL(self):
        try:
            url = self.featured_img.url
        except:
            url = ''
        return url

    @property
    def following_users_list(self):
        if self is None:
            return None
        return self.following.all()
    
    @property
    def followers_list(self):
        if self is None:
            return None
        return self.followers.all()
    
    def count_followers(self):
        return self.followers.all().count()
    
    def count_following(self):
        return self.followers.all().count()
    
    def is_following(self, username):
        return self.following_users_list.filter(
                following_user__username=username
            ).exists()
        
    def getFollowingUser(self, username):
        return self.following_users_list.filter(
                following_user__username=username
            ).first()


    class Meta:
       verbose_name = _('User')
       verbose_name_plural = _('Users')
       ordering = ['email']
       indexes = [
            models.Index(fields=['username', 'email', ])
       ]
