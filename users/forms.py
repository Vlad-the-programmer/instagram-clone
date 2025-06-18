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
        
    
class UserCreateForm(UserCreationForm):
    class Meta(UserCreationForm):
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
        widgets = {'country': CountrySelectWidget()}
        
        
        
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
        