from django import forms
from .models import Books


class BookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = ['book_title', 'rls_yn', 'wiki_gubun']
