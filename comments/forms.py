from django import forms 
from .models import Comment

class CommentCreateForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = (
            'title',
            'image',
            'content',
        )
       

class CommentUpdateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            'title',
            'image',
            'content',
        )