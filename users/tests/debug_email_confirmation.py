#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram_clone.settings')
django.setup()

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress, EmailConfirmation


def debug_configuration():
    print("=== DEBUG CONFIGURATION ===")

    # Check settings
    print(f"SITE_ID: {settings.SITE_ID}")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"ACCOUNT_EMAIL_VERIFICATION: {settings.ACCOUNT_EMAIL_VERIFICATION}")
    print(f"ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS: {settings.ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS}")

    # Check site configuration
    try:
        site = Site.objects.get(id=settings.SITE_ID)
        print(f"Site Configuration: {site.domain} (ID: {site.id})")
    except Site.DoesNotExist:
        print("❌ ERROR: Site does not exist!")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

    # Check existing email confirmations
    confirmations = EmailConfirmation.objects.all()
    print(f"\nExisting Email Confirmations: {confirmations.count()}")

    for conf in confirmations:
        print(f"  - Key: {conf.key}, Email: {conf.email_address.email}, "
              f"Expired: {conf.key_expired()}, Created: {conf.created}")

    # Check email addresses
    email_addresses = EmailAddress.objects.all()
    print(f"\nEmail Addresses: {email_addresses.count()}")

    for ea in email_addresses:
        print(f"  - Email: {ea.email}, Verified: {ea.verified}, User: {ea.user}")

    return True


if __name__ == "__main__":
    debug_configuration()