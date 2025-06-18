import logging
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

# AllAuth
from allauth.account.signals import user_signed_up, email_confirmed
from allauth.account.models import EmailAddress, EmailConfirmation

logger = logging.getLogger(__name__)


User = get_user_model()


# @receiver(post_save, sender=User)
# def save_user_profile(sender, created, instance, *args, **kwargs):
#     profile = instance
#     print(profile)
#     print(created)
#     if created == False and profile:
#         if not profile.username:
#             profile.username = profile.set_username()
#         profile.save()
                  
            
@receiver(user_signed_up)
def user_signed_up_(request, user, **kwargs):
    user.is_active = False
    # Group.objects.get(name='BlogManager').user_set.add(user)

    user.save()
    
    email_address = EmailAddress.objects.get_for_user(user, user.email)
    # Sending confirmation
    confirmation=EmailConfirmation.create(email_address)
    confirmation.send(request, signup=True)
    
    messages.add_message(
        request, 
        messages.INFO,
        message=f"Confirmation email has been sent to {user.email}",
    )
    logger.info(f"{user}'s profile created and confirm. email sent")
     
     
@receiver(email_confirmed)
def email_confirmed_(request, email_address, *args, **kwargs):
    user = User.objects.get(email=email_address.email)
    user.is_active = True
    user.save()
    
    logger.info(f"{user}'s active and confirm. email is sent")
    
    
# @receiver(post_save, sender=User)
# def update_user_profile(sender, created, instance, *args, **kwargs):
#     profile = instance
#     if not created and profile:
#         print("Worked")
#         profile.save()