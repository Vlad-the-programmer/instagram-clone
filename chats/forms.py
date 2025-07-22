from django import forms
from .models import Message, Chat


class MessageCreateUpdateForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('message', 'image')

        