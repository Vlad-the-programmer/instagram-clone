#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram_clone.settings')
django.setup()

from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress, EmailConfirmation


def simple_test():
    User = get_user_model()

    # Get or create test user
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={'first_name': 'Test', 'last_name': 'User'}
    )

    # Get or create email address
    email_addr, created = EmailAddress.objects.get_or_create(
        user=user,
        email=user.email,
        defaults={'primary': True, 'verified': False}
    )

    print(f"Initial - Verified: {email_addr.verified}")

    # Manually verify the email (bypass the confirmation process)
    email_addr.verified = True
    email_addr.save()

    print(f"After manual verification - Verified: {email_addr.verified}")

    # Test if user can login now
    from django.contrib.auth import authenticate
    auth_user = authenticate(email='test@example.com', password='testpass123')

    if auth_user:
        print("✅ User can authenticate")
        return True
    else:
        print("❌ User cannot authenticate")
        return False


if __name__ == "__main__":
    success = simple_test()
    if success:
        print("\n✅ Manual verification works!")
    else:
        print("\n❌ Manual verification failed!")