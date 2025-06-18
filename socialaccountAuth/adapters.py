from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.signals import pre_social_login
from allauth.account.utils import perform_login, complete_signup
from allauth.utils import get_user_model
from django.http import HttpResponse
from django.dispatch import receiver
from django.shortcuts import redirect
from django.conf import settings

from allauth.socialaccount.providers.oauth2.client import OAuth2Client, OAuth2Error
from allauth.socialaccount.providers.google.provider import GoogleProvider
from allauth.socialaccount.providers.google import views as google_views
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter
import jwt


class GoogleOAuth2Adapter(OAuth2Adapter):
    provider_id = GoogleProvider.id
    access_token_url = google_views.ACCESS_TOKEN_URL
    authorize_url = google_views.AUTHORIZE_URL
    id_token_issuer = google_views.ID_TOKEN_ISSUER

    def complete_login(self, request, app, token, response, **kwargs):
        try:
            identity_data = jwt.decode(
                # response["id_token"],		# removed line
                response,					# added line
                # Since the token was received by direct communication
                # protected by TLS between this library and Google, we
                # are allowed to skip checking the token signature
                # according to the OpenID Connect Core 1.0
                # specification.
                # https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation
                options={
                    "verify_signature": False,
                    "verify_iss": True,
                    "verify_aud": True,
                    "verify_exp": True,
                },
                issuer=self.id_token_issuer,
                audience=app.client_id,
            )
        except jwt.PyJWTError as e:
            raise OAuth2Error("Invalid id_token") from e
        login = self.get_provider().sociallogin_from_response(request, identity_data)
        return login
     
class MyLoginAccountAdapter(DefaultAccountAdapter):
    '''
    Overrides allauth.account.adapter.DefaultAccountAdapter.ajax_response to avoid changing
    the HTTP status_code to 400
    '''

    def get_login_redirect_url(self, request):

        if request.user.is_authenticated:
            return settings.LOGIN_REDIRECT_URL
        else:
            return "/"
        
        
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def is_open_for_signup(self, request, sociallogin):
        """
        Whether to allow sign ups.
        """
        allow_signups = super(
            CustomSocialAccountAdapter, self).is_open_for_signup(request, sociallogin)
        # Override with setting, otherwise default to super.
        return getattr(settings, 'ACCOUNT_ALLOW_SIGNUPS', allow_signups)
    

    def pre_social_login(self, request, sociallogin):

        try:
            user = Profile.objects.get(email=sociallogin.user.email)
            user.is_active = True
            user.save()
            #   request.set_cookie('auth_token', request.user.auth_token.key, domain=settings.LOGIN_REDIRECT_URL)

            sociallogin.connect(request, user)
            
        except:
            pass
    
        return None

    # def pre_social_login(self, request, sociallogin):

    #     # social account already exists, so this is just a login
    #     if sociallogin.is_existing:
    #         return

    #     # some social logins don't have an email address
    #     if not sociallogin.email_addresses:
    #         return

    #     # find the first verified email that we get from this sociallogin
    #     verified_email = None
    #     for email in sociallogin.email_addresses:
    #         if email.verified:
    #             verified_email = email
    #             break

    #     # no verified emails found, nothing more to do
    #     if not verified_email:
    #         return

    #     # check if given email address already exists as a verified email on
    #     # an existing user's account
    #     try:
    #         existing_email = EmailAddress.objects.get(email__iexact=email.email, verified=True)
    #     except EmailAddress.DoesNotExist:
    #         return

    #     # if it does, connect this new social login to the existing user
    #     sociallogin.connect(request, existing_email.user)

@receiver(pre_social_login)
def link_to_local_user(sender, request, sociallogin, **kwargs):
    ''' Login and redirect
    This is done in order to tackle the situation where user's email retrieved
    from one provider is different from already existing email in the database
    (e.g facebook and google both use same email-id). Specifically, this is done to
    tackle following issues:
    * https://github.com/pennersr/django-allauth/issues/215

    '''
    email_address = sociallogin.account.extra_data['email']
    User = get_user_model()
    users = User.objects.filter(email=email_address)
    if users:
        # allauth.account.app_settings.EmailVerificationMethod
        perform_login(request, users[0], email_verification='optional')
        raise ImmediateHttpResponse(redirect(settings.LOGIN_REDIRECT_URL))
