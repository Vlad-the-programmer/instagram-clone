#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram_clone.settings')
django.setup()

from django.conf import settings


def check_adapters():
    print("=== ADAPTERS CHECK ===")

    # Check account adapter
    account_adapter = getattr(settings, 'ACCOUNT_ADAPTER', 'allauth.account.adapter.DefaultAccountAdapter')
    print(f"ACCOUNT_ADAPTER: {account_adapter}")

    # Check social account adapter
    social_adapter = getattr(settings, 'SOCIALACCOUNT_ADAPTER',
                             'allauth.socialaccount.adapter.DefaultSocialAccountAdapter')
    print(f"SOCIALACCOUNT_ADAPTER: {social_adapter}")

    # Try to import the adapters to check if they exist
    try:
        if account_adapter != 'allauth.account.adapter.DefaultAccountAdapter':
            __import__(account_adapter.replace('.adapters', '').rsplit('.', 1)[0])
            print("✅ Custom account adapter exists")
    except ImportError as e:
        print(f"❌ Custom account adapter error: {e}")

    try:
        if social_adapter != 'allauth.socialaccount.adapter.DefaultSocialAccountAdapter':
            __import__(social_adapter.replace('.adapters', '').rsplit('.', 1)[0])
            print("✅ Custom social adapter exists")
    except ImportError as e:
        print(f"❌ Custom social adapter error: {e}")


if __name__ == "__main__":
    check_adapters()