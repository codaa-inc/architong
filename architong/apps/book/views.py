import json
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Books
from .models import Pages
from .models import Bookmark
from .forms import PostForm
from .forms import PageForm

def editor(request) :
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        # model이 아니라 form 객체를 넘겨야함
        post = PageForm()
        context = {"page": post}
        return render(request, 'editor.html', context)

def view_book(request, book_id) :
    username = request.user  # 세션으로부터 유저 정보 가져오기
    books = Books.objects.filter(book_id=book_id)
    pages = Pages.objects.filter(book_id=book_id)
    # 로그인된 사용자의 경우 페이지 정보에 북마크 등록여부 추가
    if username is not None:
        for page in pages:
            is_bookmarked = Bookmark.objects.filter(page_id=page.page_id, username=username).count()
            if is_bookmarked > 0:
                page.is_bookmarked = 1
            else:
                page.is_bookmarked = 0
    context = {'books': books, 'pages': pages}
    return render(request, 'viewer.html', context)

@login_required(login_url="/account/google/login")
@csrf_exempt
def add_or_remove_bookmark(request, page_id):
    if request.user.is_authenticated:
        # 해당 북마크가 존재하는지 select
        select_count = Bookmark.objects.filter(page_id=page_id, username=request.user).count()
        # 등록된 북마크가 있으면 delete
        if select_count > 0:
            delete_bm = Bookmark.objects.get(page_id=page_id, username=request.user)
            delete_bm.delete()
            result = 'delete'
        # 등록된 북마크가 없으면 insert
        else:
            insert_bm = Bookmark()  # 모델 객체 생성
            insert_bm.page_id = page_id
            insert_bm.username = request.user
            insert_bm.save()
            result = 'insert'
    else:
        result = 'false'
    context = {"result": result}
    return JsonResponse(context)

