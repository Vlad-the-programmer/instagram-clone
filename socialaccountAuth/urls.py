from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView
from django.urls import path

from .adapters import GoogleOAuth2AdapterIdToken
from .views import GoogleLogin

app_name = "socialaccountAuth"
urlpatterns = [
    path(
        "login/google/",
        GoogleLogin.as_view(),
        name="google_login"
    ),
    path(
        "login/google/callback/",
        OAuth2CallbackView.adapter_view(GoogleOAuth2AdapterIdToken),
        name="google_callback"
    ),
]