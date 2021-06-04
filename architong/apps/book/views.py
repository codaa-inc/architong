import json
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Books, Pages, Bookmark
from apps.forum.models import Comments
from .forms import PostForm, PageForm


# 마크다운 편집 페이지 렌더링 function
def editor(request):
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


# 책 조회 function
def view_book(request, book_id):
    username = request.user  # 세션으로부터 유저 정보 가져오기
    books = Books.objects.filter(book_id=book_id)
    pages = Pages.objects.filter(book_id=book_id)
    # 페이지별 댓글 count 추가
    for page in pages:
        q = Q()
        q.add(Q(page_id=page.page_id), q.AND)
        q.add(~Q(status="D"), q.AND)
        q.add(~Q(status="TD"), q.AND)
        q.add(Q(page_id=page.page_id, rls_yn="Y") | Q(page_id=page.page_id, rls_yn="N", username=username), q.AND)
        comment_count = Comments.objects.filter(q).count()
        page.comment_count = comment_count
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


# 페이지 조회 function
def view_page(request, page_id):
    username = request.user  # 세션으로부터 유저 정보 가져오기
    book_id = Pages.objects.get(page_id=page_id).book_id
    books = Books.objects.filter(book_id=book_id)
    pages = Pages.objects.filter(book_id=book_id)
    # 페이지별 댓글 count 추가
    for page in pages:
        q = Q()
        q.add(Q(page_id=page.page_id), q.AND)
        q.add(~Q(status="D"), q.AND)
        q.add(~Q(status="TD"), q.AND)
        q.add(Q(page_id=page.page_id, rls_yn="Y") | Q(page_id=page.page_id, rls_yn="N", username=username), q.AND)
        comment_count = Comments.objects.filter(q).count()
        page.comment_count = comment_count
    # 로그인된 사용자의 경우 페이지 정보에 북마크 등록여부 추가
    if username is not None:
        for page in pages:
            is_bookmarked = Bookmark.objects.filter(page_id=page.page_id, username=username).count()
            if is_bookmarked > 0:
                page.is_bookmarked = 1
            else:
                page.is_bookmarked = 0
    context = {'books': books, 'pages': pages, 'page_id': str(page_id)}
    return render(request, 'viewer.html', context)


# 북마크 등록 / 삭제 function
@csrf_exempt
def add_or_remove_bookmark(request, page_id):
    del_comment = []
    message = ""
    if request.user.is_authenticated:
        username = request.user
        # 해당 북마크가 존재하는지 select
        bookmark = Bookmark.objects.filter(page_id=page_id, username=username)
        # 등록된 북마크가 있으면 delete
        if bookmark.count() > 0:
            # 북마크 하위 메모들을 삭제한다
            private_comment = Comments.objects.filter(Q(page_id=page_id, username=username, rls_yn="N") & ~Q(status="D"))
            del_comment = list(private_comment.values())
            for data in private_comment:
                data.status = "D"
            Comments.objects.bulk_update(private_comment, ['status'])
            # 북마크를 삭제한다
            delete_bm = Bookmark.objects.get(page_id=page_id, username=request.user)
            delete_bm.delete()
            result = 'delete'
        # 등록된 북마크가 없으면 insert
        else:
            insert_bm = Bookmark()  # 모델 객체 생성
            insert_bm.page_id = page_id
            insert_bm.book_id = Pages.objects.get(page_id=page_id).book_id
            insert_bm.username = request.user
            insert_bm.save()
            result = 'insert'
    else:
        result = 'false'
        print("result : ", result)
        message = "로그인이 필요한 서비스입니다.\n로그인하시겠습니까?"
    context = {"result": result, "del_comment": del_comment, "message": message}
    return JsonResponse(context)


# 댓글 갯수를 리턴해주는 function
@login_required
def comment_count(request):
    if request.method == 'GET':
        page_id = request.GET['page_id']
        rls_yn = request.GET['rls_yn']
        username = request.user
        count = Comments.objects.filter(
            Q(page_id=page_id) & Q(rls_yn=rls_yn) & Q(username=username) & ~Q(status='D')).count()
        return JsonResponse({"result": str(count)})