#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram_clone.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from allauth.account.models import EmailAddress, EmailConfirmation
from django.utils.timezone import now
from django.test import RequestFactory
from django.urls import reverse


def test_actual_confirmation():
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

    # Create confirmation
    confirmation = EmailConfirmation.create(email_addr)
    confirmation.sent = now()
    confirmation.save()

    print("=== TEST ACTUAL CONFIRMATION ===")
    print(f"Key: {confirmation.key}")

    # Get the correct URL using reverse with the key parameter
    try:
        confirm_url = reverse('account_confirm_email', kwargs={'key': confirmation.key})
        print(f"URL: http://127.0.0.1:8000{confirm_url}")
    except Exception as e:
        print(f"❌ URL reverse error: {e}")
        return False

    # Test if we can access the confirmation view directly
    factory = RequestFactory()
    request = factory.get(confirm_url)

    # Add user to request if needed
    if hasattr(request, 'user'):
        request.user = user

    try:
        # Import the view function correctly
        from allauth.account.views import ConfirmEmailView
        from django.http import HttpRequest

        # Create a proper request object
        real_request = HttpRequest()
        real_request.method = 'GET'
        real_request.META['SERVER_NAME'] = '127.0.0.1'
        real_request.META['SERVER_PORT'] = '8000'

        # Create the view and call it properly
        view = ConfirmEmailView()
        view.setup(real_request, key=confirmation.key)

        # Get the response
        response = view.get(real_request, key=confirmation.key)

        print(f"Response status: {response.status_code}")
        if hasattr(response, 'url'):
            print(f"Redirect to: {response.url}")

        # Check if email is now verified
        email_addr.refresh_from_db()
        print(f"Email verified after confirmation: {email_addr.verified}")

        return True

    except Exception as e:
        print(f"❌ Error during confirmation: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_actual_confirmation()
    if success:
        print("\n✅ Confirmation process works!")
    else:
        print("\n❌ Confirmation process failed!")