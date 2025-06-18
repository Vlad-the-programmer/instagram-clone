from django.shortcuts import redirect
from django.conf import settings
# Auth
from django.contrib import messages

    
def login_required(view_func, login_url=settings.LOGIN_URL):  
    def wrapper(request, *args, **kwargs):
        print("Request user: ", request.user)
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        if not request.user.is_authenticated:
            messages.info(request, "Login first!")
            return redirect(login_url)
    return wrapper