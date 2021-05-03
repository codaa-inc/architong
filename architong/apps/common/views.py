from django.shortcuts import render
from django.conf import settings
'''
from apps.common.models import Post
from apps.common.forms import PostForm
'''

def index(request):
    return render(request, 'index.html')
