from django.core.management.base import BaseCommand
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Check email confirmations in the database'

    def handle(self, *args, **options):
        self.stdout.write("\n=== Checking Email Confirmations ===")
        
        # Check if we have a site configured
        try:
            site = Site.objects.get_current()
            self.stdout.write(f"Current site: {site.domain} (ID: {site.id})")
        except Site.DoesNotExist:
            self.stdout.write("Error: No sites configured. Please run 'python manage.py migrate' and set up a site in the admin.")
            return
        
        # Check email confirmations
        confirmations = EmailConfirmation.objects.all()
        self.stdout.write(f"\nFound {confirmations.count()} email confirmation(s) in the database:")
        
        for i, conf in enumerate(confirmations, 1):
            self.stdout.write(f"\nEmail Confirmation {i}:")
            self.stdout.write(f"  Email: {conf.email_address}")
            self.stdout.write(f"  Created: {conf.created}")
            self.stdout.write(f"  Sent: {conf.sent}")
            self.stdout.write(f"  Key: {conf.key}")
            
            # Generate the confirmation URL
            try:
                hmac = EmailConfirmationHMAC(conf)
                confirm_url = f"http://{site.domain}/accounts/confirm-email/{hmac.key}/"
                self.stdout.write(f"  Confirmation URL: {confirm_url}")
            except Exception as e:
                self.stdout.write(f"  Error generating URL: {str(e)}")
        
        self.stdout.write("\n=== End of Email Confirmations ===\n")
