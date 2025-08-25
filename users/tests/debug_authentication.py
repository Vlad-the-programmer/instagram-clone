#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram_clone.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate


def debug_authentication():
    User = get_user_model()

    print("=== AUTHENTICATION DEBUG ===")

    # Check if user exists
    try:
        user = User.objects.get(email='test@example.com')
        print(f"✅ User exists: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   Has password: {bool(user.password)}")
        print(f"   Is active: {user.is_active}")
        print(f"   Is staff: {user.is_staff}")
        print(f"   Is superuser: {user.is_superuser}")

    except User.DoesNotExist:
        print("❌ User does not exist")
        return False
    except Exception as e:
        print(f"❌ Error getting user: {e}")
        return False

    # Test authentication
    print("\n🔐 Testing authentication:")

    # Test with correct password
    auth_user = authenticate(email='test@example.com', password='testpass123')
    if auth_user:
        print("✅ Authentication successful with correct password")
    else:
        print("❌ Authentication failed with correct password")

    # Test password check directly
    print(f"   Password check: {user.check_password('testpass123')}")

    # Check what authentication backends are available
    from django.conf import settings
    print(f"\n🔧 Authentication backends:")
    for backend in settings.AUTHENTICATION_BACKENDS:
        print(f"   - {backend}")

    return auth_user is not None


if __name__ == "__main__":
    success = debug_authentication()
    if success:
        print("\n✅ Authentication works!")
    else:
        print("\n❌ Authentication failed!")