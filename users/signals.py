import logging
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

# AllAuth
from allauth.account.signals import user_signed_up, email_confirmed
from allauth.account.models import EmailAddress, EmailConfirmation

logger = logging.getLogger(__name__)


Profile = get_user_model()
                  
            
@receiver(user_signed_up)
def user_signed_up_(request, user, **kwargs):
    user.is_active = False

    user.save()
    
    email_address = EmailAddress.objects.get_for_user(user, user.email)
    # Sending confirmation
    confirmation=EmailConfirmation.create(email_address)
    confirmation.send(request, signup=True)
    
    messages.add_message(
        request, 
        messages.INFO,
        message=f"Confirmation email has been sent to {user.email}",
    )
    logger.info(f"{user}'s profile created and confirm. email sent")
     
     
@receiver(email_confirmed)
def email_confirmed_(request, email_address, *args, **kwargs):
    user = Profile.objects.get(email=email_address.email)
    user.is_active = True
    user.save()
    
    logger.info(f"{user}'s active and confirm. email is sent")


@receiver(post_save, sender=Profile)
def add_default_permissions(sender, instance, created, **kwargs):
    # if created:
        # Get the permission codenames from get_user_perms
        permission_codenames = [
            codename for codename, has_perm in instance.get_user_perms().items()
            if has_perm and codename != 'admin' and codename != 'chat'
        ]
        print(permission_codenames)
        # Get the actual Permission objects
        basic_perms = Permission.objects.filter(codename__in=permission_codenames)

        # Assign permissions to the user
        instance.user_permissions.add(*basic_perms)  # Note the * to unpack queryset
        print(instance.user_permissions.all())
        # Handle group creation and assignment
        basic_group, created = Group.objects.get_or_create(name='Basic Users')
        if created:
            # Add permissions to the group (must use set() with IDs)
            basic_group.permissions.set(basic_perms.values_list('id', flat=True))

        # Add user to group
        instance.groups.add(basic_group)