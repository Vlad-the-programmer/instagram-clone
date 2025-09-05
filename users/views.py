from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
# Auth
from django.contrib.auth import get_user_model
from django.contrib import messages
# Generic class-based views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import detail, edit, TemplateView

# Allauth
from allauth.account.views import SignupView

from .emails_handler import send_verification_email
from .forms import SignUpForm, UserUpdateForm
from . import mixins as custom_mixins
from common import mixins as common_mixins

Profile = get_user_model()


class RegisterView(SignupView):
    form_class = SignUpForm
    success_url = reverse_lazy('users:email-confirmation-sent')
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
        print(f"User created: {self.user}")
        print(f"User email: {self.user.email}")
        print(f"User active status: {self.user.is_active}")

        return response

class EmailConfirmationSentView(TemplateView):
    template_name = 'account/email/email_confirmation_info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email_sent'] = self.request.GET.get('email_sent', False)
        return context

class ProfileDetailView(LoginRequiredMixin,
                        custom_mixins.GetProfileObjectMixin,
                        common_mixins.HandleNotFoundObjectMixin,
                        detail.DetailView):
    model = Profile
    template_name = 'profile/profile_detail.html'
    context_object_name = 'profile'

class ProfileDeleteView(LoginRequiredMixin,
                        custom_mixins.GetProfileObjectMixin,
                        common_mixins.HandleNotFoundObjectMixin,
                        common_mixins.InvalidFormMixin,
                        edit.DeleteView):
    template_name = 'profile/profile_delete.html'
    success_url = reverse_lazy('users:register')

    def form_valid(self, form):
        messages.success(self.request, 'Profile deleted!')
        return redirect(self.success_url)

class ProfileUpdateView(LoginRequiredMixin,
                        custom_mixins.GetProfileObjectMixin,
                        common_mixins.HandleNotFoundObjectMixin,
                        common_mixins.InvalidFormMixin,
                        edit.UpdateView):
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
