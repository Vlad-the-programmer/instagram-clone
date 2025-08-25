#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram_clone.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.account.models import EmailConfirmation


def fix_configuration():
    print("=== FIXING CONFIGURATION ===")

    # Fix site configuration
    site, created = Site.objects.get_or_create(
        id=1,
        defaults={
            'domain': '127.0.0.1:8000',
            'name': 'localhost'
        }
    )

    if not created:
        site.domain = '127.0.0.1:8000'
        site.name = 'localhost'
        site.save()

    print(f"✅ Site configured: {site.domain} (ID: {site.id})")

    # Clear all old email confirmations
    count = EmailConfirmation.objects.all().count()
    EmailConfirmation.objects.all().delete()
    print(f"✅ Cleared {count} old email confirmations")

    print("\n✅ Configuration fixed! Please restart your server and try again.")


if __name__ == "__main__":
    fix_configuration()
