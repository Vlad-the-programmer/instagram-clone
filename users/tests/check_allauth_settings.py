#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram_clone.settings')
django.setup()

from django.conf import settings


def check_allauth_settings():
    print("=== ALLAUTH SETTINGS CHECK ===")

    critical_settings = [
        'ACCOUNT_EMAIL_VERIFICATION',
        'ACCOUNT_EMAIL_REQUIRED',
        'ACCOUNT_CONFIRM_EMAIL_ON_GET',
        'ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS',
        'ACCOUNT_AUTHENTICATION_METHOD',
        'ACCOUNT_USERNAME_REQUIRED',
        'SITE_ID',
        'ACCOUNT_DEFAULT_HTTP_PROTOCOL'
    ]

    for setting in critical_settings:
        value = getattr(settings, setting, 'NOT SET')
        print(f"{setting}: {value}")

    # Check if email confirmation is enabled
    if hasattr(settings, 'ACCOUNT_EMAIL_VERIFICATION'):
        if settings.ACCOUNT_EMAIL_VERIFICATION == 'mandatory':
            print("✅ Email verification is mandatory")
        else:
            print(f"⚠️  Email verification is: {settings.ACCOUNT_EMAIL_VERIFICATION}")

    # Check site configuration
    try:
        from django.contrib.sites.models import Site
        site = Site.objects.get(id=settings.SITE_ID)
        print(f"✅ Site configured: {site.domain} (ID: {site.id})")
    except Exception as e:
        print(f"❌ Site error: {e}")


if __name__ == "__main__":
    check_allauth_settings()