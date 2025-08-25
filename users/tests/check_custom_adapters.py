#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram_clone.settings')
django.setup()


def check_custom_adapters():
    print("=== CUSTOM ADAPTERS CONTENT ===")

    # Try to inspect the custom adapters
    try:
        from socialaccountAuth.adapters import CustomSocialAccountAdapter, MyLoginAccountAdapter

        print("✅ Custom adapters imported successfully")

        # Check if they override confirmation methods
        for adapter_class in [CustomSocialAccountAdapter, MyLoginAccountAdapter]:
            print(f"\n🔍 Checking {adapter_class.__name__}:")

            # Check if they override email confirmation methods
            if hasattr(adapter_class, 'confirm_email'):
                print("   ❌ Overrides confirm_email method - THIS MAY BE THE PROBLEM")
            else:
                print("   ✅ Does not override confirm_email method")

            if hasattr(adapter_class, 'save_user'):
                print("   ⚠️  Overrides save_user method")
            else:
                print("   ✅ Does not override save_user method")

    except ImportError as e:
        print(f"❌ Cannot import custom adapters: {e}")
    except Exception as e:
        print(f"❌ Error checking adapters: {e}")


if __name__ == "__main__":
    check_custom_adapters()
    