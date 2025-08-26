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
