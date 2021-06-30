from django import forms
from martor.fields import MartorFormField
from .models import Books, Pages


class BookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = ['book_title', 'rls_yn']


class PageForm(forms.ModelForm):
    page_title = forms.CharField(widget=forms.TextInput())

    class Meta:
        model = Pages
        fields = '__all__'
