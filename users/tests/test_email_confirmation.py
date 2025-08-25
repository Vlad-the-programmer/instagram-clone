#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram_clone.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from allauth.account.models import EmailAddress, EmailConfirmation
from django.utils.timezone import now


def test_email_confirmation():
    User = get_user_model()

    # Get the current site
    current_site = Site.objects.get_current()

    # Create test user
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()

    # Create email address
    email_addr, created = EmailAddress.objects.get_or_create(
        user=user,
        email=user.email,
        defaults={'primary': True, 'verified': False}
    )

    # Create confirmation
    confirmation = EmailConfirmation.create(email_addr)
    confirmation.sent = now()
    confirmation.save()

    print("=== TEST EMAIL CONFIRMATION ===")
    print(f"Current Site: {current_site.domain} (ID: {current_site.id})")
    print(f"User: {user.email}")
    print(f"Email Address ID: {email_addr.id}")
    print(f"Confirmation Key: {confirmation.key}")
    print(f"Confirmation URL: http://127.0.0.1:8000/accounts/confirm-email/{confirmation.key}/")
    print(f"Expired: {confirmation.key_expired()}")
    print(f"Created: {confirmation.created}")

    # Test if the confirmation is valid
    is_valid = not confirmation.key_expired()
    print(f"Key is valid: {is_valid}")

    return is_valid


if __name__ == "__main__":
    success = test_email_confirmation()
    if success:
        print("\n✅ Test passed! The confirmation should work.")
    else:
        print("\n❌ Test failed! The confirmation is expired.")