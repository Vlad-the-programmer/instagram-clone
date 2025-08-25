from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ( 
                                        UserCreationForm, 
                                        UserChangeForm, 
                                        ReadOnlyPasswordHashField
                                    )
from django_countries.widgets import CountrySelectWidget
from django.utils.translation import gettext_lazy as _
from allauth.account import forms as login_form
# # Signal 
# from django.db.models.signals import post_save
# from .signals import update_user_profile
from chats.models import Message
from allauth.account.forms import SignupForm

Profile = get_user_model()


class UserUpdateForm(UserChangeForm):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user’s password, but you can change the password using "
        ),
    )
    featured_img = forms.ImageField(required=False)
    class Meta:
        model = Profile
        fields = (
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'country',
                  'featured_img',
                  'gender',
                  )
    
    # def save(self, *args, **kwargs):
    #     profile = super().save(commit=False)
    #     post_save.disconnect(update_user_profile, sender=Profile)
    #     profile.save()
    #     post_save.connect(update_user_profile, sender=Profile)


from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from allauth.account.forms import SignupForm
from .models import Profile, GenderChoices
import re

from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from allauth.account.forms import SignupForm
from .models import Profile, GenderChoices
import re


class SignUpForm(SignupForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name',
            'autocomplete': 'given-name'
        }),
        help_text="Required. 30 characters or fewer."
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name',
            'autocomplete': 'family-name'
        }),
        help_text="Required. 30 characters or fewer."
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })
    )

    country = CountryField().formfield(
        required=True,
        widget=CountrySelectWidget(attrs={
            'class': 'form-select',
            'style': 'width: 100%;'
        }),
        help_text="Select your country of residence."
    )

    gender = forms.ChoiceField(
        choices=GenderChoices,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    featured_img = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text="Upload a profile picture. Optional."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field if it exists from parent class
        if 'username' in self.fields:
            del self.fields['username']

        # Reorder fields if needed
        self.fields['email'].widget.attrs.update({'autofocus': ''})

        # Add Bootstrap classes to allauth's default fields
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({
                'class': 'form-control',
                'placeholder': 'Create a password'
            })
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({
                'class': 'form-control',
                'placeholder': 'Confirm your password'
            })

    def generate_unique_username(self, base_username):
        """Generate a unique username by appending numbers if needed"""
        username = base_username
        counter = 1
        while Profile.objects.filter(username__iexact=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        return username

    def clean(self):
        """Generate username from email and validate it"""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if email:
            # Generate username from email
            base_username = email.split('@')[0]

            # Clean the username (remove special characters, etc.)
            base_username = re.sub(r'[^a-zA-Z0-9_\.]', '', base_username)

            # Ensure username is not empty
            if not base_username:
                base_username = "user"

            # Generate unique username
            username = self.generate_unique_username(base_username)

            # Validate username format
            if not re.match(r'^[\w.@+-]+$', username):
                raise forms.ValidationError(
                    "Generated username contains invalid characters."
                )

            # Store the generated username in cleaned_data
            cleaned_data['username'] = username

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists
            if Profile.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError("A user with that email already exists.")
        return email

    def save(self, request):
        # Call the parent save method to create the user
        user = super().save(request)

        # Update the user profile with additional fields
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.country = self.cleaned_data['country']
        user.gender = self.cleaned_data['gender']

        # Set the auto-generated username
        user.username = self.cleaned_data['username']

        # Handle profile image upload
        if 'featured_img' in self.cleaned_data and self.cleaned_data['featured_img']:
            user.featured_img = self.cleaned_data['featured_img']

        user.save()
        return user

    class Meta:
        model = Profile
        fields = (
            'email',
            'first_name',
            'last_name',
            'country',
            'featured_img',
            'gender',
        )
        
        
class UserLoginForm(login_form.LoginForm):
    class Meta:
        def __init__(self):
            super(login_form.LoginForm, self).__init__()
            for field in self.fields:
                field.update({'class': 'form-control'})
        

class UserPasswordResetForm(forms.ModelForm):
    confirm_password = forms.PasswordInput(attrs={'placeholder': 'Confirm password'})
    class Meta:
        model = Profile
        fields = ('password',)
        widgets = {'password': forms.PasswordInput(attrs={'placeholder': 'New password'})}
        