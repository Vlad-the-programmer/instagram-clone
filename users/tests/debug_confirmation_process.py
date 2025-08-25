#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram_clone.settings')
django.setup()

from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress, EmailConfirmation
from django.utils.timezone import now
from django.test import RequestFactory
from django.urls import reverse


def debug_confirmation_process():
    User = get_user_model()

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

    print(f"Before confirmation - Email verified: {email_addr.verified}")

    # Create confirmation
    confirmation = EmailConfirmation.create(email_addr)
    confirmation.sent = now()
    confirmation.save()

    print(f"Confirmation key: {confirmation.key}")
    print(f"Confirmation created: {confirmation.created}")
    print(f"Confirmation sent: {confirmation.sent}")
    print(f"Key expired: {confirmation.key_expired()}")

    # Test the confirmation
    confirm_url = reverse('account_confirm_email', kwargs={'key': confirmation.key})
    print(f"Confirmation URL: http://127.0.0.1:8000{confirm_url}")

    # Simulate the confirmation request
    factory = RequestFactory()
    request = factory.get(confirm_url)

    # Add user to request
    request.user = user

    try:
        # Import and call the confirmation view
        from allauth.account.views import confirm_email
        response = confirm_email(request, confirmation.key)

        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content[:200]}...")  # First 200 chars

        # Refresh and check email status
        email_addr.refresh_from_db()
        print(f"After confirmation - Email verified: {email_addr.verified}")

        # Check if confirmation was deleted (which happens on success)
        try:
            confirmation.refresh_from_db()
            print("Confirmation still exists")
        except EmailConfirmation.DoesNotExist:
            print("Confirmation was deleted (this indicates success)")

        return email_addr.verified

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = debug_confirmation_process()
    if success:
        print("\n✅ Email was successfully verified!")
    else:
        print("\n❌ Email was NOT verified!")