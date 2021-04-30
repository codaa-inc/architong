from django.shortcuts import render
from django.conf import settings
'''
from apps.common.models import Post
from apps.common.forms import PostForm
'''

def index(request):
    return render(request, 'index.html')

'''
def editor(request) :
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            #  delete and insert
            md = form.save(commit=False)
            md.markdown_save()
    else:
        # model이 아니라 form 객체를 넘겨야함
        post = PostForm()
        context = {"page": post}
        return render(request, 'editor.html', context)

def viewer(request) :
    post = Post.objects.last()
    context = {'post': post}
    return render(request, 'viewer.html', context)
'''