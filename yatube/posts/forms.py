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

    def clean_text(self):
        data = self.cleaned_data['text']
        if not data:
            raise data.ValidationError('Поле комментария должно быть '
                                       'заполнено')
        return data
