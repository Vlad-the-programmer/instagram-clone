from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.conf import settings
# Auth
from django.contrib import messages

    
    
class LoginRequiredMixin():
    def get(self, request, *args, **kwargs):
        print("Request user: ", request.user)
        if not request.user.is_authenticated:
            messages.info(request, "Login first!")
            return redirect(settings.LOGIN_URL)
        return super().get(request, *args, **kwargs)