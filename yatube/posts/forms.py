from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'text',
            'group',
            'image',
        ]
        widgets = {
            'text': forms.Textarea(attrs={
                'maxlength': '700',
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'maxlength': '300',
            }),
        }
