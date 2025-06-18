from django import forms
from .models import Like


class LikeCreateDeleteForm(forms.ModelForm):
    post = forms.HiddenInput()
    class Meta:
        model = Like
        fields = ("post",)