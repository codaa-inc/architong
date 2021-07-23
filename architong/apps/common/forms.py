from django import forms
from apps.book.models import Pages


class LawForm(forms.ModelForm):
    class Meta:
        model = Pages
        fields = ['page_title', 'description']
