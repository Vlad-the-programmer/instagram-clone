import logging

from django.shortcuts import redirect
from django.conf import settings
# Auth
from django.contrib import messages

logger = logging.getLogger(__name__)

class LoginRequiredMixin:
    """Custom authentication mixin that adds messages"""
    def dispatch(self, request, *args, **kwargs):
        print("Request user: ", request.user)
        if not request.user.is_authenticated:
            messages.info(request, "Login first!")
            return redirect(settings.LOGIN_URL)
        return super().dispatch(request, *args, **kwargs)
