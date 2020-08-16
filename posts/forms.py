from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Post
from django.forms import ModelForm


#revision
class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text']
        labels = {
            'group': _('Группа'),
            'text': _('Текст'),
        }

form = PostForm()
