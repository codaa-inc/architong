import json
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages

from apps.forum.models import Comments
from .forms import BookForm, PostForm, PageForm
from .models import Books, Pages, Bookmark


# 책만들기 function
def wiki_register(request):
    # GET 요청이면 책만들기 페이지 렌더링
    if request.method == 'GET':
        return render(request, "book/wiki_register.html")

    # POST 요청이면 책저장하고 페이지 에디터로 렌더링
    elif request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            # 신규 book 객체 저장
            new_book = Books(
                author_id=request.user, codes_yn="N",
                book_title=request.POST.get('book_title'),
                rls_yn=request.POST.get('rls_yn')
            )
            new_book.save()
            book_id = Books.objects.order_by('book_id').last().book_id
            return JsonResponse({"book_id": book_id})
        else:
            return JsonResponse({"error_message": "책제목은 최소 3글자, 최대 255글자 입니다."})


# 마크다운 편집 페이지 렌더링 function
def wiki_editor(request, book_id):
    # GET 요청이면 editor 페이지 렌더링
    if request.method == 'GET':
        book = Books.objects.get(book_id=book_id)
        return render(request, 'book/editor.html', {"page": PageForm(), "book": book})

    # POST 요청
    elif request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            parent_id = request.POST.get('parent_id', 0)
            page = Pages(
                book_id=book_id, page_title=request.POST.get('page_title'),
                description=request.POST.get('description'),
                parent_id=parent_id,
                depth=0 if parent_id == 0 else 1
            )
            page_id = Pages.objects.order_by('page_id').last().page_id
            page.save()
            return JsonResponse({"page_id": page_id})
        else:
            return JsonResponse({"error_message": "오류메세지작성"})


# 마크다운 에디터 미리보기 모드
def wiki_page_editor(request, page_id):
    return render(request, 'book/editor.html')


# 법규 리스트 조회 function
def law_list(request):
    sort = request.GET.get('sort', 'recent')  # 정렬기준 쿼리스트링을 가져온다, 없는 경우 default 시행일자순
    if sort == 'views':
        laws = Books.objects.filter(codes_yn="Y", rls_yn="Y").order_by('-enfc_dt')
    elif sort == 'registered':
        laws = Books.objects.filter(codes_yn="Y", rls_yn="Y").order_by('enfc_dt')
    else:
        laws = Books.objects.filter(codes_yn="Y", rls_yn="Y").order_by('-enfc_dt')

    # 페이징처리
    page = request.GET.get('page')
    paginator = Paginator(laws, 15).get_page(page)

    # 정렬기준
    sort_list = [{'value': 'recent', 'label': '시행일순'},
                 {'value': 'views', 'label': '조회순'},
                 {'value': 'registered', 'label': '과거순'}]
    if sort != 'recent':
        for idx, item in enumerate(sort_list):
            if item.get('value') == sort:
                sel_item = sort_list[idx]
                sort_list.remove(sel_item)
                sort_list.insert(0, sel_item)

    context = {"books": paginator, "sort_list": sort_list}
    return render(request, "book/law_list.html", context)


# 문서 리스트 조회 function
def wiki_list(request):
    sort = request.GET.get('sort', 'recent')  # 정렬기준 쿼리스트링을 가져온다, 없는 경우 default 등록순
    if sort == 'views':
        docs = Books.objects.filter(codes_yn="N", rls_yn="Y").order_by('-wrt_dt')
    elif sort == 'registered':
        docs = Books.objects.filter(codes_yn="N", rls_yn="Y").order_by('wrt_dt')
    else:
        docs = Books.objects.filter(codes_yn="N", rls_yn="Y").order_by('-wrt_dt')

    # 페이징처리
    page = request.GET.get('page')
    paginator = Paginator(docs, 15).get_page(page)

    # 정렬기준
    sort_list = [{'value': 'recent', 'label': '등록순'},
                 {'value': 'views', 'label': '조회순'},
                 {'value': 'registered', 'label': '과거순'}]
    if sort != 'recent':
        for idx, item in enumerate(sort_list):
            if item.get('value') == sort:
                sel_item = sort_list[idx]
                sort_list.remove(sel_item)
                sort_list.insert(0, sel_item)
    context = {"books": paginator, "sort_list": sort_list}
    return render(request, "book/wiki_list.html", context)


# 책 조회 function
def view_book(request, book_id):
    # Books, Pages QuerySet
    username = request.user
    book = Books.objects.get(book_id=book_id)
    pages = Pages.objects.filter(book_id=book_id)

    # 본문 장의 갯수 → 1개의 장으로 구성되어 있는 경우 제목 보여주지 않기 위함
    law_count = pages.filter(Q(depth=0) & ~Q(page_title="별표/서식")).count()

    # 페이지별 댓글 count 추가
    for page in pages:
        q = Q(page_id=page.page_id)
        q.add(~Q(status="D") & ~Q(status="TD"), q.AND)
        q.add(Q(page_id=page.page_id, rls_yn="Y") | Q(page_id=page.page_id, rls_yn="N", username=username), q.AND)
        page.comment_count = Comments.objects.filter(q).count()

    # 로그인된 사용자의 경우 페이지 정보에 북마크 등록여부 추가
    if username is not None:
        for page in pages:
            is_bookmarked = Bookmark.objects.filter(page_id=page.page_id, username=username).count()
            if is_bookmarked > 0:
                page.is_bookmarked = 1
            else:
                page.is_bookmarked = 0

    context = {'book': book,
               'pages': pages,
               'law_count': law_count}
    return render(request, 'book/viewer.html', context)


# 페이지 조회 function
def view_page(request, page_id):
    # Books, Pages QuerySet
    username = request.user  # 세션으로부터 유저 정보 가져오기
    book_id = Pages.objects.get(page_id=page_id).book_id
    book = Books.objects.get(book_id=book_id)
    pages = Pages.objects.filter(book_id=book_id)

    # 본문 장의 갯수 → 1개의 장으로 구성되어 있는 경우 제목 보여주지 않기 위함
    law_count = pages.filter(Q(depth=0) & ~Q(page_title="별표/서식")).count()

    # 페이지별 댓글 count 추가
    for page in pages:
        q = Q(page_id=page.page_id)
        q.add(~Q(status="D") & ~Q(status="TD"), q.AND)
        q.add(Q(rls_yn="Y") | Q(rls_yn="N", username=username), q.AND)
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

    context = {'book': book,
               'pages': pages,
               'page_id': str(page_id),
               'law_count': law_count}
    return render(request, 'book/viewer.html', context)


# 북마크 등록, 삭제 function
@csrf_exempt
def add_or_remove_bookmark(request, page_id):
    del_comment = []
    message = ""
    if request.user.is_authenticated:
        # 해당 북마크가 존재하는지 select
        username = request.user
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

    # 비인가 사용자 로그인 페이지로 redirect
    else:
        result = 'false'
        message = "로그인이 필요한 서비스입니다.\n로그인하시겠습니까?"

    context = {"result": result,
               "del_comment": del_comment,
               "message": message}
    return JsonResponse(context)


# 북마크 관리 페이지 조회 function
@login_required(login_url="/account/google/login")
def view_bookmark(request):
    username = request.user  # 세션으로부터 유저 정보 가져오기
    if username is not None:
        bookmarks = Bookmark.objects.filter(username=username).order_by('book_id', 'page_id')
        page_q = Q(page_id__in=bookmarks.values_list('page_id', flat=True))
        status_q = Q(status="C") | Q(status="U")
        pages = Pages.objects.filter(page_q).values()
        comments = Comments.objects.filter(page_q & status_q & Q(rls_yn="N"))
        for idx, bookmark in enumerate(bookmarks):
            bookmark.description = pages.get(page_id=bookmark.page_id)['description']
            comment = comments.filter(page_id=bookmark.page_id).values()
            if len(comment) > 0:
                bookmark.comment = json.dumps(list(comment), cls=DjangoJSONEncoder)
            if idx == 0 or bookmark.book_id != bookmarks[idx - 1].book_id:
                bookmark.book_title = Books.objects.get(book_id=bookmark.book_id).book_title
        return render(request, "book/bookmark.html", {"bookmarks": bookmarks})


# 북마크 관리 페이지 삭제 function
@login_required(login_url="/account/google/login")
@csrf_exempt
def delete_bookmark(request, page_id):
    username = request.user  # 세션으로부터 유저 정보 가져오기
    if username is not None:
        # 북마크 하위 메모들을 삭제한다
        private_comment = Comments.objects.filter(page_id=page_id, username=username, rls_yn="N")
        for data in private_comment:
            data.status = "D"
        Comments.objects.bulk_update(private_comment, ['status'])
        # 북마크를 삭제한다
        bookmark = Bookmark.objects.get(page_id=page_id, username=username)
        bookmark.delete()
        return JsonResponse({"result": "success"})


# 댓글 갯수를 리턴해주는 function
@login_required
def comment_count(request):
    if request.method == 'GET':
        page_id = request.GET['page_id']
        rls_yn = request.GET['rls_yn']
        username = request.user
        q = Q(page_id=page_id) & Q(rls_yn=rls_yn) & Q(username=username) & ~Q(status='D')
        count = Comments.objects.filter(q).count()
        return JsonResponse({"comment_count": str(count)})
