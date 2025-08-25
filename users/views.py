from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
# Auth
from django.contrib.auth import get_user_model
from django.contrib import messages
# Generic class-based views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import detail, edit
# Email verification 
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
# Allauth
from allauth.account.views import SignupView

from .emails_handler import send_verification_email
from .forms import SignUpForm, UserUpdateForm
from . import mixins as custom_mixins
from common import mixins as common_mixins


Profile = get_user_model()

class RegisterView(SignupView):
    # template_name = 'auth/register.html'
    form_class = SignUpForm

    def form_valid(self, form):
        response = super().form_valid(form)
        # Sending email activation
        # mail_subject = 'Please activate your account'
        # template_email = 'accounts/account_verification_email.html'
        # send_verification_email(self.request,
        #                         self.request.user,
        #                         template_email,
        #                         mail_subject,
        #                         is_activation_email=True)
        return response

class ProfileDetailView(custom_mixins.GetProfileObjectMixin,
                        common_mixins.HandleNotFoundObjectMixin,
                        detail.DetailView
                    ):
    model = Profile
    template_name = 'profile/profile_detail.html'
    context_object_name = 'profile'
        

class ProfileDeleteView(LoginRequiredMixin,
                        custom_mixins.GetProfileObjectMixin,
                        common_mixins.HandleNotFoundObjectMixin,
                        common_mixins.InvalidFormMixin,
                        edit.DeleteView
                    ):
    template_name = 'profile/profile_delete.html'
    success_url = reverse_lazy('users:register')

        
    def form_valid(self, form):
            messages.success(self.request, 'Profile deleted!')
            return redirect(self.success_url)


class ProfileUpdateView(LoginRequiredMixin,
                        custom_mixins.GetProfileObjectMixin,
                        common_mixins.HandleNotFoundObjectMixin,
                        common_mixins.InvalidFormMixin,
                        edit.UpdateView
                    ):
    template_name = 'profile/profile-update.html'
    form_class = UserUpdateForm

    def form_valid(self, form):
        """Handle valid form submission and add success message."""
        response = super().form_valid(form)
        messages.success(self.request, 'Your profile has been updated!')
        return response

    def get_success_url(self):
        profile = self.get_object()
        success_url = reverse('users:profile-detail', kwargs={
                                                            'pk': profile.id
                                                        }
                              )
        return success_url

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if Profile.get_user_by_email(email=email):
            user = get_object_or_404(Profile, email__exact=email)
            
            # Reset password email
            mail_subject = 'Reset Your Password'
            
            template_email = 'accounts/reset_password_email.html'
            send_verification_email(request, user, template_email, mail_subject)
            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('users:login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('users:forgotPassword'), 400
        
    return render(request, 'accounts/forgotPassword.html')


def reset_password_validate(request, pk):
    try:
        user = get_object_or_404(Profile, id=pk)
    except (Profile.DoesNotExist, ValueError):
        user = None

    if user is not None:
        messages.success(request, 'Please reset your password')
        return redirect(reverse('users:resetPassword', kwargs={'pk': pk}))
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('users:login')


def resetPassword(request, pk):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password == confirm_password:
            user = get_object_or_404(Profile, id=pk)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('users:login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect(reverse('users:resetPassword', kwargs={'pk': pk}))
    else:
        return render(request, 'accounts/resetPassword.html', context={'pk': pk})


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(Profile, id=uid)
    except (TypeError, ValueError, OverflowError, Profile.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect(reverse_lazy('users:login'))
    else:
        messages.error(request, 'Invalid activation link')
        return redirect(reverse_lazy('users:register'))

# def register(request):
#     if request.method == 'POST':
#         form = UserCreateForm(request.POST, request.FILES)
#
#         if form.is_valid():
#             user = form.save(commit=False)
#
#             if Profile.get_user_by_email(user.email):
#                 messages.info(request, 'User already exists!')
#                 return redirect(reverse_lazy('users:login'))
#
#             user.save()
#
#             # Sending email activation
#             mail_subject = 'Please activate your account'
#             template_email = 'accounts/account_verification_email.html'
#             send_verification_email(request,
#                                     user,
#                                     template_email,
#                                     mail_subject,
#                                     is_activation_email=True)
#         else:
#             messages.error(request, f'{form.errors}')
#             return redirect(reverse_lazy('users:register'))
#
#     else:
#         form = UserCreateForm()
#
#     context = {}
#     context['form'] = form
#     return render(request, 'auth/register.html', context)
