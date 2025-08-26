from django.contrib.auth.models import AbstractUser
from django.http.request import HttpRequest
from django.http.response import HttpResponsePermanentRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
# Verification email
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib import messages


def send_verification_email(request: HttpRequest, user: AbstractUser, template_email,
                            mail_subject=None, is_activation_email=False) -> HttpResponsePermanentRedirect:
    """
        Send verification/activation email with token
        Params:
            request: HttpRequest
            user: AbstractUser recipient
            template_email: str template_file name for email
            mail_subject: str
    """

    uuid = urlsafe_base64_encode(force_bytes(user.id))
    token = default_token_generator.make_token(user)
    current_site = get_current_site(request)
    message = render_to_string(template_email, {
        'user': user,
        'domain': current_site,
        'uid': uuid,
        'token': token,
    })
    to_email = user.email
    
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()
    
    if is_activation_email:
        messages.success(request, f'Thank you. We have sent you a verification\
            email to your email address {to_email}. Please verify it.'
        )
        return redirect('/accounts/login/?command=verification&email='+to_email)
    else:
        messages.success(request, f'Thank you. We have sent you an email with \
        the instructions to your email address {to_email}. Please check it.'
        )
        return redirect(reverse_lazy('users:login'))

    
    