#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram_clone.settings')
django.setup()

from django.urls import reverse, NoReverseMatch


def check_urls():
    print("=== URL CONFIGURATION CHECK ===")

    # Check all AllAuth URLs
    allauth_urls = [
        'account_login',
        'account_signup',
        'account_logout',
        'account_confirm_email',
        'account_reset_password',
        'account_email'
    ]

    for url_name in allauth_urls:
        try:
            url = reverse(url_name)
            print(f"✅ {url_name}: {url}")
        except NoReverseMatch as e:
            print(f"❌ {url_name}: {e}")

    # Check if allauth URLs are included
    from django.urls import get_resolver
    resolver = get_resolver()

    print("\n=== URL PATTERNS ===")
    for pattern in resolver.url_patterns:
        if hasattr(pattern, 'url_patterns'):  # It's an include
            print(f"📁 {pattern.pattern}: {pattern.namespace}")
            for subpattern in pattern.url_patterns:
                print(f"   └── {subpattern.pattern}: {getattr(subpattern, 'name', 'No name')}")
        else:
            print(f"📄 {pattern.pattern}: {getattr(pattern, 'name', 'No name')}")


if __name__ == "__main__":
    check_urls()