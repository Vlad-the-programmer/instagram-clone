import logging

from allauth.core.internal.httpkit import redirect
from django.contrib import messages
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

# AllAuth
from allauth.account.signals import user_signed_up, email_confirmation_sent, email_confirmed
from allauth.account.models import EmailAddress, EmailConfirmation

from users.permissions import PermissionEnum

logger = logging.getLogger(__name__)

Profile = get_user_model()


@receiver(user_signed_up)
def user_signed_up_(request, user, **kwargs):
    user.is_active = False
    user.save()

    email_address = EmailAddress.objects.get_for_user(user, user.email)

    # Use EmailConfirmationHMAC for proper key generation
    from allauth.account.models import EmailConfirmationHMAC
    confirmation = EmailConfirmationHMAC(email_address)
    confirmation.send(request, signup=True)

    messages.add_message(
        request,
        messages.INFO,
        message=f"Confirmation email has been sent to {user.email}",
    )
    logger.info(f"{user}'s profile created and confirm. email sent")

@receiver(email_confirmed)
def email_confirmed_(request, email_address, **kwargs):
    """
    Activate the user when their email is confirmed
    """
    user = email_address.user
    user.is_active = True
    user.save()
    logger.info(f"{user}'s email confirmed and account activated")

@receiver(post_save, sender=Profile)
def add_default_permissions(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.is_superuser:
        logger.info(f"Superuser {instance.username} created with full permissions")
        return

    if instance.is_staff:
        staff_group, _ = Group.objects.get_or_create(name='Staff')
        excluded_content_types = ContentType.objects.filter(
            app_label__in=['admin', 'auth', 'contenttypes', 'sessions']
        )
        staff_perms = Permission.objects.exclude(
            content_type__in=excluded_content_types
        )
        staff_group.permissions.add(*staff_perms)
        instance.groups.add(staff_group)
        logger.info(f"Staff user {instance.username} added to Staff group")
        return

    basic_permission_codenames = [perm.value for perm in PermissionEnum]
    logger.info(f"Permission codenames: {basic_permission_codenames}")

    basic_perms = Permission.objects.filter(codename__in=basic_permission_codenames)
    logger.info(f"basic perms: {basic_perms}")

    instance.user_permissions.add(*basic_perms)
    logger.info(f"User permissions: {instance.user_permissions.all()}")

    basic_group, created = Group.objects.get_or_create(name='Basic Users')
    if created:
        basic_group.permissions.set(basic_perms.values_list('id', flat=True))
        logger.info(f"Group permissions: {basic_group.permissions.all()}")
    instance.groups.add(basic_group)