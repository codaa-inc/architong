import json
import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q

from apps.forum.models import Comments
from .forms import BookForm, PageForm
from .models import Books, Pages, Bookmark


# 나의 위키 페이지 렌더링
@login_required(login_url="/account/google/login")
def wiki_manage(request):
    username = str(request.user)
    sort = request.GET.get('sort', 'recent')  # 정렬기준 쿼리스트링을 가져온다, 없는 경우 default 등록순
    if sort == 'views':
        docs = Books.objects.filter(codes_yn="N", author_id=username).order_by('-hit_count')
    elif sort == 'registered':
        docs = Books.objects.filter(codes_yn="N", author_id=username).order_by('wrt_dt')
    else:
        docs = Books.objects.filter(codes_yn="N", author_id=username).order_by('-mdfcn_dt')

    # 댓글 객체 좋아요 관련 정보 추가 : is_liked, like_user_count
    for doc in docs:
        like_comment = list(Books.objects.get(book_id=doc.book_id).like_users.all())
        if request.user in like_comment:
            doc.is_liked = "true"
        else:
            doc.is_liked = "false"
        doc.like_user_count = len(like_comment)

    # 페이징처리
    page = request.GET.get('page')
    paginator = Paginator(docs, 15).get_page(page)

    # 정렬기준
    sort_list = [{'value': 'recent', 'label': '최근 편집순'},
                 {'value': 'views', 'label': '조회순'},
                 {'value': 'registered', 'label': '작성순'}]
    if sort != 'recent':
        for idx, item in enumerate(sort_list):
            if item.get('value') == sort:
                sel_item = sort_list[idx]
                sort_list.remove(sel_item)
                sort_list.insert(0, sel_item)
    context = {"books": paginator, "sort_list": sort_list}
    return render(request, "book/wiki_manage.html", context)


# 책만들기 function
@login_required(login_url="/account/google/login")
def wiki_add(request):
    # GET 요청이면 책만들기 페이지 렌더링
    if request.method == 'GET':
        return render(request, "book/wiki_regist.html")
    # POST 요청이면 책저장하고 페이지 에디터로 렌더링
    elif request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            # 신규 book 객체 저장
            new_book = Books(
                author_id=request.user,
                book_title=request.POST.get('book_title'),
                rls_yn=request.POST.get('rls_yn'),
                codes_yn="N",
            )
            new_book.save()
            book_id = Books.objects.order_by('book_id').last().book_id
            return JsonResponse({"book_id": book_id})
        else:
            return JsonResponse({"error_message": "책제목은 최소 3글자, 최대 255글자 입니다."})


# 책정보 조회/수정 function
@login_required(login_url="/account/google/login")
def wiki_update(request, book_id):
    book = Books.objects.get(book_id=book_id)
    # 작성자와 사용자가 일치하는지 체크
    if str(request.user) == book.author_id:
        # GET 요청이면 책정보 페이지 조회
        if request.method == 'GET':
            # 목차 계층구조 정렬
            sorted_pages = []
            parent_pages = Pages.objects.filter(book_id=book.book_id, depth=0)
            child_pages = Pages.objects.filter(book_id=book.book_id, depth=1)
            for parent_page in parent_pages:
                sorted_pages.append(parent_page)
                for child_page in child_pages:
                    if child_page.parent_id == parent_page.page_id:
                        sorted_pages.append(child_page)
            # 댓글 객체 좋아요 관련 정보 추가 : is_liked, like_user_count
            like_comment = list(book.like_users.all())
            if request.user in like_comment:
                book.is_liked = "true"
            else:
                book.is_liked = "false"
            book.like_user_count = len(like_comment)
            # 댓글 갯수
            page_list = Pages.objects.filter(book_id=book_id).values_list('page_id')
            comment_count = Comments.objects.filter(page_id__in=page_list).count()
            book.comment_count = comment_count
            context = {"book": book,
                       "page_list": sorted_pages}
            return render(request, "book/editor.html", context)
        elif request.method == 'POST':
            form = BookForm(request.POST)
            if form.is_valid():
                book.book_title = request.POST.get('book_title')
                book.rls_yn = request.POST.get('rls_yn')
                book.wiki_gubun = request.POST.get('wiki_gubun')
                book.save()
                return JsonResponse({"result": "success", "message": "위키정보가 저장되었습니다."})
            else:
                return JsonResponse({"result": "fail", "message": "정보를 확인해주세요."})


# 마크다운 에디터 페이지 추가 function
@login_required(login_url="/account/google/login")
def wiki_add_page(request, book_id):
    book = Books.objects.get(book_id=book_id)
    # 작성자와 사용자가 일치하는지 체크
    if str(request.user) == book.author_id:
        # GET 요청이면 editor 새로운 페이지 생성 후 페이지 렌더링
        if request.method == 'GET':
            # 새로운 페이지 등록
            new_page = Pages(
                book_id=book_id,
                parent_id=request.GET.get('page', 0),
                depth=1 if request.GET.get('page') else 0,
                page_title="페이지 제목"
            )
            new_page.save()
            book.mdfcn_dt = datetime.datetime.now().now()
            book.save()  # 해당 위키의 최근수정일 갱신
            new_page = Pages.objects.order_by('page_id').last()
            # 목차 계층구조 정렬
            sorted_pages = []
            parent_pages = Pages.objects.filter(book_id=book.book_id, depth=0)
            child_pages = Pages.objects.filter(book_id=book.book_id, depth=1)
            for parent_page in parent_pages:
                sorted_pages.append(parent_page)
                for child_page in child_pages:
                    if child_page.parent_id == parent_page.page_id:
                        sorted_pages.append(child_page)
            context = {"page_form": PageForm(instance=new_page),
                       "page_id":  new_page.page_id,
                       "book": book,
                       "page_list": sorted_pages}
            return render(request, 'book/editor.html', context)
    else:
        return HttpResponse("잘못된 접근입니다.")


# 마크다운 에디터 function
@login_required(login_url="/account/google/login")
def wiki_editor(request, page_id):
    page = Pages.objects.get(page_id=page_id)
    book = Books.objects.get(book_id=page.book_id)
    # 작성자와 사용자가 일치하는지 체크
    if str(request.user) == book.author_id:
        # GET 요청이면 에디터 페이지 랜더링
        if request.method == 'GET':
            # 목차 계층구조 정렬
            sorted_pages = []
            parent_pages = Pages.objects.filter(book_id=book.book_id, depth=0)
            child_pages = Pages.objects.filter(book_id=book.book_id, depth=1)
            for parent_page in parent_pages:
                sorted_pages.append(parent_page)
                for child_page in child_pages:
                    if child_page.parent_id == parent_page.page_id:
                        sorted_pages.append(child_page)
            context = {"page_form": PageForm(instance=page),
                       "page_id":  page.page_id,
                       "book": book,
                       "page_list": sorted_pages}
            return render(request, 'book/editor.html', context)
        # POST 요청이면 페이지 수정 저장
        elif request.method == 'POST':
            form = PageForm(request.POST)
            if form.is_valid():
                page = Pages.objects.get(page_id=page_id)
                page.page_title = request.POST['page_title']
                page.description = request.POST['description']
                page.save()
                book.mdfcn_dt = datetime.datetime.now().now()
                book.save()     # 해당 위키의 최근수정일 갱신
                return JsonResponse({"page_id": page_id})
            else:
                return JsonResponse({"error_message": "양식을 확인해주세요."})
    else:
        return HttpResponse("잘못된 접근입니다.")


# 마크다운 에디터 미리보기 모드 function
@login_required(login_url="/account/google/login")
def wiki_page_viewer(request, page_id):
    page = Pages.objects.get(page_id=page_id)
    book = Books.objects.get(book_id=page.book_id)
    # 작성자와 사용자가 일치하는지 체크
    if str(request.user) == book.author_id:
        # GET 요청이면 미리보기 페이지 랜더링
        if request.method == 'GET':
            sorted_pages = []
            parent_pages = Pages.objects.filter(book_id=book.book_id, depth=0)
            child_pages = Pages.objects.filter(book_id=book.book_id, depth=1)
            # 페이지 계층구조 정렬
            for parent_page in parent_pages:
                sorted_pages.append(parent_page)
                for child_page in child_pages:
                    if child_page.parent_id == parent_page.page_id:
                        sorted_pages.append(child_page)
            context = {
                "book": book,
                "page_list": sorted_pages,
                "page": page
            }
            return render(request, 'book/editor.html', context)
    else:
        return HttpResponse("잘못된 접근입니다.")


# 위키 삭제 function
@login_required(login_url="/account/google/login")
def wiki_delete(request, book_id):
    book = Books.objects.get(book_id=book_id)
    # 작성자와 사용자가 일치하는지 체크
    if str(request.user) == book.author_id:
        # 연관 북마크 삭제
        Bookmark.objects.filter(book_id=book_id).delete()
        # 연관 댓글 삭제
        page_list = Pages.objects.filter(book_id=book_id)
        for page in page_list:
            Comments.objects.filter(page_id=page.page_id).delete()
        # 하위 페이지들 삭제
        page_list.delete()
        # 페이지 삭제
        book.delete()
        return JsonResponse({"result": "success"})
    else:
        return HttpResponse("잘못된 접근입니다.")


# 위키 페이지 삭제 function
@login_required(login_url="/account/google/login")
def wiki_delete_page(request, page_id):
    page = Pages.objects.get(page_id=page_id)
    book = Books.objects.get(book_id=page.book_id)
    # 작성자와 사용자가 일치하는지 체크
    if str(request.user) == book.author_id:
        # 연관 북마크 삭제
        Bookmark.objects.filter(page_id=page_id).delete()
        # 연관 댓글 삭제
        Comments.objects.filter(page_id=page_id).delete()
        # 자식 페이지 삭제
        Pages.objects.filter(parent_id=page_id).delete()
        # 페이지 삭제
        page.delete()
        # 해당 위키의 최근수정일 갱신
        book.mdfcn_dt = datetime.datetime.now().now()
        book.save()
        return JsonResponse({"book_id": book.book_id})
    else:
        return HttpResponse("잘못된 접근입니다.")


# 법규 리스트 조회 function
def law_list(request):
    sort = request.GET.get('sort', 'recent')  # 정렬기준 쿼리스트링을 가져온다, 없는 경우 default 시행일자순
    if sort == 'views':
        laws = Books.objects.filter(codes_yn="Y", rls_yn="Y").order_by('-hit_count')
    elif sort == 'registered':
        laws = Books.objects.filter(codes_yn="Y", rls_yn="Y").order_by('enfc_dt')
    else:
        laws = Books.objects.filter(codes_yn="Y", rls_yn="Y").order_by('-enfc_dt')

    # 댓글 객체 좋아요 관련 정보 추가 : is_liked, like_user_count
    for law in laws:
        like_comment = list(Books.objects.get(book_id=law.book_id).like_users.all())
        if request.user in like_comment:
            law.is_liked = "true"
        else:
            law.is_liked = "false"
        law.like_user_count = len(like_comment)

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
    context = {"books": paginator,
               "sort_list": sort_list}
    return render(request, "book/lawlist.html", context)


# 문서 리스트 조회 function
def wiki_list(request):
    sort = request.GET.get('sort', 'recent')  # 정렬기준 쿼리스트링을 가져온다, 없는 경우 default 등록순
    if sort == 'views':
        docs = Books.objects.filter(codes_yn="N", rls_yn="Y").order_by('-hit_count')
    elif sort == 'registered':
        docs = Books.objects.filter(codes_yn="N", rls_yn="Y").order_by('wrt_dt')
    else:
        docs = Books.objects.filter(codes_yn="N", rls_yn="Y").order_by('-wrt_dt')

    # 댓글 객체 좋아요 관련 정보 추가 : is_liked, like_user_count
    for doc in docs:
        like_comment = list(Books.objects.get(book_id=doc.book_id).like_users.all())
        if request.user in like_comment:
            doc.is_liked = "true"
        else:
            doc.is_liked = "false"
        doc.like_user_count = len(like_comment)

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
    return render(request, "book/wikilist.html", context)


# 책/페이지 조회 function
def view_book(request, book_id):
    # Books, Pages QuerySet
    username = request.user
    book = Books.objects.get(book_id=book_id)
    pages = Pages.objects.filter(book_id=book_id)

    # 본문 장의 갯수 → 1개의 장으로 구성되어 있는 경우 제목 보여주지 않기 위함
    law_count = pages.filter(Q(depth=0) & ~Q(page_title="별표/서식")).count()

    # 댓글 객체 좋아요 관련 정보 추가 : is_liked, like_user_count
    like_comment = list(book.like_users.all())
    if request.user in like_comment:
        book.is_liked = "true"
    else:
        book.is_liked = "false"
    book.like_user_count = len(like_comment)

    # 댓글 count 추가
    total_comment_count = 0
    for page in pages:
        q = Q(page_id=page.page_id)
        q.add(~Q(status="D") & ~Q(status="TD"), q.AND)
        q.add(Q(rls_yn="Y") | Q(rls_yn="N", username=username), q.AND)
        comment_count = Comments.objects.filter(q).count()
        page.comment_count = comment_count
        total_comment_count += comment_count
    book.total_comment_count = total_comment_count

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

    # Cookie 생성 후 조회수 증감
    session_cookie = request.user
    cookie_name = F'comment_hits:{session_cookie}'
    response = render(request, 'book/viewer.html', context)

    if request.COOKIES.get(cookie_name) is not None:
        cookies = request.COOKIES.get(cookie_name)
        cookies_list = cookies.split('|')
        if str(book_id) not in cookies_list:
            response.set_cookie(cookie_name, cookies + f'|{book_id}', expires=None)
            book.hit_count += 1
            book.save()
            return response
    else:
        response.set_cookie(cookie_name, book_id, expires=None)
        book.hit_count += 1
        book.save()
        return response

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

    # 댓글 객체 좋아요 관련 정보 추가 : is_liked, like_user_count
    like_comment = list(book.like_users.all())
    if request.user in like_comment:
        book.is_liked = "true"
    else:
        book.is_liked = "false"
    book.like_user_count = len(like_comment)

    # 댓글 count 추가
    total_comment_count = 0
    for page in pages:
        q = Q(page_id=page.page_id)
        q.add(~Q(status="D") & ~Q(status="TD"), q.AND)
        q.add(Q(rls_yn="Y") | Q(rls_yn="N", username=username), q.AND)
        comment_count = Comments.objects.filter(q).count()
        page.comment_count = comment_count
        total_comment_count += comment_count
    book.total_comment_count = total_comment_count

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

    # Cookie 생성 후 조회수 증감
    session_cookie = request.user
    cookie_name = F'comment_hits:{session_cookie}'
    response = render(request, 'book/viewer.html', context)

    if request.COOKIES.get(cookie_name) is not None:
        cookies = request.COOKIES.get(cookie_name)
        cookies_list = cookies.split('|')
        if str(book_id) not in cookies_list:
            response.set_cookie(cookie_name, cookies + f'|{book_id}', expires=None)
            book.hit_count += 1
            book.save()
            return response
    else:
        response.set_cookie(cookie_name, book_id, expires=None)
        book.hit_count += 1
        book.save()
        return response
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
            private_comment = Comments.objects.filter(
                Q(page_id=page_id, username=username, rls_yn="N") & ~Q(status="D"))
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
            insert_bm = Bookmark(
                page_id=page_id,
                book_id=Pages.objects.get(page_id=page_id).book_id,
                username=request.user
            )
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
    page_id = request.GET['page_id']
    rls_yn = request.GET['rls_yn']
    username = request.user
    q = Q(page_id=page_id) & Q(rls_yn=rls_yn) & Q(username=username) & ~Q(status='D')
    count = Comments.objects.filter(q).count()
    return JsonResponse({"comment_count": str(count)})


# 책 좋아요 토글 function
@login_required(login_url="/account/google/login")
def like_book(request, book_id):
    # 문서, 작성자 QuerySet 선언
    book = Books.objects.get(book_id=book_id)
    author = get_user_model().objects.get(username=book.author_id)

    # 좋아요 삭제, 댓글 작성자 활동점수 -1
    if request.user in book.like_users.all():
        book.like_users.remove(request.user)
        author.act_point = int(author.act_point) - 1
        author.save()
        result = "remove"
    # 좋아요 등록, 댓글 작성자 활동점수 +1
    else:
        book.like_users.add(request.user)
        author.act_point = int(author.act_point) + 1
        author.save()
        result = "add"
    return JsonResponse({"result": result})



def testmd(request):
    return render(request, "book/testmd.html")

