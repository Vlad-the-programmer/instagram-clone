from django import forms
from .models import Post, Tags


class UpdateForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        required = False,
        queryset=Tags.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        )
    class Meta:
        model = Post
        fields = ('title', 'content', 'image', 'tags')
        

class CreateForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        required = False,
        queryset=Tags.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        )
    class Meta:
        model = Post
        fields = ('title', 'content', 'image', 'tags')
        