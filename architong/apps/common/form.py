from django import forms
from django.db import models
from martor.fields import MartorFormField

class PostForm(forms.Form):
    title = models.CharField(max_length=255)
    description = MartorFormField()
