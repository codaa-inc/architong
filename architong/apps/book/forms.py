from django import forms
from martor.fields import MartorFormField
from apps.book.models import Pages


class PageForm(forms.Form):
    page_title = forms.CharField(widget=forms.TextInput())
    description = MartorFormField()

class PostForm(forms.ModelForm):
    class Meta:
        model = Pages
        fields = '__all__'
