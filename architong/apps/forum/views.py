import json
import datetime
from typing import List

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator
from django.db.models import Q, Subquery, OuterRef, Count
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View

from apps.forum.models import Comments, UserLikeComment
from apps.book.models import Books, Pages, Bookmark
from apps.common.models import SocialaccountSocialaccount as Socialaccount


# 댓글 조회 / 등록 / 삭제 class
class CommentView(View):
    # GET 요청시 해당 페이지의 댓글 조회
    def get(self, request, id):
        comments = []
        username = request.user

        # 유효한 페이지인지 검증
        try:
            page = Pages.objects.get(page_id=id)
        except Pages.DoesNotExist:
            return render(request, "404.html", {"message": "잘못된 접근입니다."})

        # 부모,자식 댓글 QuerySet
        q = Q(page_id=id) & ~Q(status="D")
        if username.is_authenticated:
            q.add(Q(rls_yn="Y") | Q(rls_yn="N", username=username), q.AND)
        else:
            q.add(Q(rls_yn="Y"), q.AND)
        parent_node = Comments.objects.filter(Q(depth=0) & q).values()
        child_node = Comments.objects.filter(Q(depth=1) & q).values()

        # 부모 댓글 > 자식 댓글 : 계층형 데이터 정렬
        for parent in parent_node:
            if parent['status'] == "TD":
                parent.content = "이 댓글은 삭제되었습니다."
            comments.append(parent)
            for child in child_node:
                if child['parent_id'] == parent['comment_id']:
                    comments.append(child)

        # 좋아요 관련 정보 추가 : is_liked, like_user_count
        for comment in comments:
            like_comment = Comments.objects.get(comment_id=comment['comment_id']).like_users.all()
            if request.user in like_comment:
                comment['is_liked'] = "true"
            else:
                comment['is_liked'] = "false"
            comment['like_user_count'] = len(like_comment)

        context = json.dumps(comments, cls=DjangoJSONEncoder)
        return HttpResponse(context, content_type="text/json")

    # POST 요청시 댓글 등록
    def post(self, request, id):
        # Comment 객체 선언, ID 지정
        comment = Comments()
        nodestr = id.split('-')[0]
        idstr = id.split('-')[1]
        username = request.user

        # 유효한 페이지인지 검증
        try:
            page = Pages.objects.get(page_id=idstr)
        except Pages.DoesNotExist:
            return render(request, "404.html", {"message": "잘못된 접근입니다."})

        # 해당 댓글의 작성자와 일치하는지 검증
        if username.is_authenticated:
            # 부모,자식 댓글에 공통으로 저장할 data
            comment.username = username
            comment.content = request.POST['content']
            comment.status = "C"

            # 부모댓글에 저장할 data
            if nodestr == 'parent':
                comment.depth = 0
                comment.parent_id = 0
                page_id = idstr
                comment.page_id = idstr
                rls_yn = request.POST['rls_yn']
                comment.rls_yn = rls_yn

            # 자식댓글에 저장할 data
            elif nodestr == 'child':
                comment.depth = 1
                comment.parent_id = idstr
                comment.page_id = Comments.objects.filter(comment_id=idstr).values('page_id')
                # 자식댓글의 공개여부는 부모댓글을 따라간다.
                rls_yn = Comments.objects.filter(comment_id=idstr).values('rls_yn')
                comment.rls_yn = rls_yn

            # 비공개 메모 등록시 해당 페이지가 북마크에 없으면 북마크를 등록한다.
            if rls_yn == "N":
                bookmark_count = Bookmark.objects.filter(page_id=page_id, username=username).count()
                if bookmark_count == 0:
                    bookmark = Bookmark()
                    bookmark.page_id = page_id
                    bookmark.book_id = Pages.objects.get(page_id=page_id).book_id
                    bookmark.username = username
                    bookmark.save()

            # 공개 댓글 등록시 작성자의 활동점수를 +2 증감시킨다.
            else:
                user_info = get_user_model().objects.get(username=username)
                user_info.act_point = user_info.act_point + 2
                user_info.save()
            comment.save()

            # 저장한 comment 객체를 return
            comment_id = Comments.objects.order_by('-pk')[0].comment_id
            new_comment_obj = Comments.objects.filter(comment_id=comment_id).values()

            # 공개댓글에 좋아요 관련 정보 추가 : is_liked, like_user_count
            for new_comment in new_comment_obj:
                if new_comment['rls_yn'] == "Y":
                    like_comment = Comments.objects.get(comment_id=comment_id).like_users.all()
                    if request.user in like_comment:
                        new_comment['is_liked'] = "true"
                    else:
                        new_comment['is_liked'] = "false"
                    new_comment['like_user_count'] = len(like_comment)

            context = json.dumps(list(new_comment_obj), cls=DjangoJSONEncoder)
            return HttpResponse(context, content_type="text/json")
        else:
            # 비인가 접근은 로그인 페이지로 redirect
            message = "잘못된 접근입니다.\n로그인하시겠습니까?"
            context = {"result": "fail", "message": message}
            return JsonResponse(context, content_type="text/json")

    # DELETE 요청시 댓글 삭제
    def delete(self, request, id):
        username = request.user
        comment_id = id.split('-')[1]

        # Comments 쿼리셋
        try:
            comment = Comments.objects.get(comment_id=comment_id)
        except Comments.DoesNotExist:
            return render(request, "404.html", {"message": "존재하지 않는 댓글입니다."})

        # 해당 댓글의 작성자와 일치하는지 검증
        if username.is_authenticated and str(username) == comment.username:
            result = "delete"
            status = Q(status="C") | Q(status="U")
            # 자식 댓글이 존재하는 경우 → 임시삭제 상태로 변경
            if comment.depth == 0:
                has_any_child = Comments.objects.filter(Q(parent_id=comment_id) & status).count()
                if has_any_child > 0:
                    comment.status = "TD"
                    comment.save()
                    result = "temporary delete"
                    return JsonResponse({"result": result})

            # 부모 댓글이 임시삭제 상태이면서 형제 댓글이 없을 때 → 부모 댓글을 삭제 상태로 변경
            elif comment.depth == 1:
                parent = Comments.objects.get(comment_id=comment.parent_id)
                sibling_count = Comments.objects.filter(Q(parent_id=comment.parent_id) & status).count()
                if parent.status == "TD" and sibling_count <= 1:
                    parent.status = "D"
                    parent.save()
                    result = "parent delete"

            # 해당 댓글을 삭제 상태로 변경
            comment.status = "D"
            comment.save()
            return JsonResponse({"result": result})
        else:
            return render(request, "404.html", {"message": "잘못된 접근입니다."})


# 댓글 수정 function
@login_required(login_url="/account/google/login")
def comment_update(request, id):
    # Comment 객체 선언, ID 지정
    try:
        comment_id = id.split('-')[1]
        comment = Comments.objects.get(comment_id=comment_id)
    except Comments.DoesNotExist:
        return render(request, "404.html", {"message": "존재하지 않는 댓글입니다."})

    if request.method == 'POST' and str(request.user) == comment.username:
        # 댓글을 수정한다.
        comment.content = request.POST['content']
        comment.reg_dt = datetime.datetime.now()
        comment.status = "U"
        comment.save()

        # 저장한 comment 객체를 return 한다.
        update_comment_obj = list(Comments.objects.filter(comment_id=comment_id).values())[0]
        # 공개댓글에 좋아요 관련 정보 추가 : is_liked, like_user_count
        if update_comment_obj['rls_yn'] == "Y":
            like_comment = Comments.objects.get(comment_id=comment_id).like_users.all()
            update_comment_obj['like_user_count'] = len(like_comment)
            if request.user in like_comment:
                update_comment_obj['is_liked'] = "true"
            else:
                update_comment_obj['is_liked'] = "false"
        return HttpResponse(json.dumps(update_comment_obj, cls=DjangoJSONEncoder), content_type="text/json")
    else:
        return render(request, "404.html", {"message": "잘못된 접근입니다."})


# 포럼 리스트 조회 function
def forum(request):
    # 쿼리셋 호출
    keyword = request.GET.get('keyword', '')  # 검색어 쿼리스트링을 가져온다, 없는 경우 공백
    sort = request.GET.get('sort', 'recent')  # 정렬기준 쿼리스트링을 가져온다, 없는 경우 default 최신순
    q = Q(depth=0) & Q(rls_yn='Y') & (Q(status="C") | Q(status="U")) & Q(content__icontains=keyword)
    q_child = Q(depth=1) & Q(rls_yn='Y') & (Q(status="C") | Q(status="U"))

    if sort == 'popular':  # 인기순
        comments = Comments.objects.annotate(
            like_user_count=Coalesce(Subquery(
                UserLikeComment.objects.filter(comment_id=OuterRef('pk')).values('comment_id').annotate(
                    count=Count('pk')).values('count')
            ), 0)).filter(q).order_by('-like_user_count', '-reg_dt')
    elif sort == 'comments':  # 댓글순
        comments = Comments.objects.annotate(comments=Coalesce(Subquery(
            Comments.objects.filter(parent_id=OuterRef('pk')).values('parent_id').annotate(
                count=Count('pk')).values('count')
        ), 0)).filter(q).order_by('-comments', '-reg_dt')
    elif sort == 'views':  # 조회순
        comments = Comments.objects.filter(q).order_by('-hit_count', '-reg_dt')
    else:
        comments = Comments.objects.filter(q).order_by('-reg_dt')

    comments: List[Comments] = list(comments)
    child_comments: List[Comments] = list(Comments.objects.filter(q_child).only('parent_id'))
    socialaccount: List[Socialaccount] = list(Socialaccount.objects.all().only('user_id', 'extra_data'))
    books: List[Books] = list(Books.objects.all().only('book_id', 'book_title'))
    pages: List[Pages] = list(Pages.objects.all())

    for comment in comments:
        page = [page for page in pages if page.page_id == comment.page_id]

        # 댓글 객체 작성자 프로필 사진 정보 추가 : picture
        user_id = get_user_model().objects.get(username=comment.username).id
        extra_data = [account.extra_data for account in socialaccount if account.user_id == user_id][0]
        comment.picture = json.loads(extra_data)['picture']

        # 댓글 객체 관련 법규 정보 추가 : page_id, page_title
        book_title = [book for book in books if book.book_id == page[0].book_id][0].book_title
        comment.page_title = "[" + str(book_title).replace(" ", "") + "] " + str(page[0].page_title)
        comment.page_id = page[0].page_id

        # 댓글 객체 좋아요 관련 정보 추가 : is_liked, like_user_count
        like_comment = list(comment.like_users.all())
        if request.user in like_comment:
            comment.is_liked = "true"
        else:
            comment.is_liked = "false"
        if sort != "popular":
            comment.like_user_count = len(like_comment)

        # 자식댓글 갯수 추가
        child_count = [child for child in child_comments if child.parent_id == comment.comment_id]
        comment.child_count = len(child_count)

    # 정렬기준 (템플릿에서 정렬기준을 selectbox 대신 div > a로 표현하기 위함)
    sort_list = [{'value': 'recent', 'label': '최신순'},
                 {'value': 'popular', 'label': '인기순'},
                 {'value': 'comments', 'label': '댓글순'},
                 {'value': 'views', 'label': '조회순'}]
    if sort != 'recent':
        for idx, item in enumerate(sort_list):
            if item.get('value') == sort:
                sel_item = sort_list[idx]
                sort_list.remove(sel_item)
                sort_list.insert(0, sel_item)

    # 페이징 처리
    if request.GET.get('page') is None:
        page = 1
    else:
        page = request.GET.get('page')
    paginator = Paginator(comments, 10).get_page(page)

    context = {"comments": paginator,
               "comments_count": str(len(comments)),
               "keyword": keyword,
               "sort_list": sort_list}
    return render(request, 'forum/forum.html', context)


# 포럼 상세 조회 function
def forum_detail(request, comment_id):
    # 자식댓글 조회 여부 초기값 false
    child_view = False

    # 부모댓글 QuerySet
    try:
        parent_comment = Comments.objects.get(comment_id=comment_id)
    except Comments.DoesNotExist:
        return render(request, "404.html", {"message": "존재하지 않는 게시물입니다."})
    if parent_comment.depth == 1:
        # 자식댓글로 호출이 들어온 경우 부모댓글을 찾아가고, 자식조회 flag 설정함
        parent_id = parent_comment.parent_id
        parent_comment = Comments.objects.get(comment_id=parent_id)
        child_view = comment_id
        comment_id = parent_id

    # 부모,자식 공통 QuerySet 호출
    users = list(get_user_model().objects.all().only('id', 'username'))
    socialaccounts: List[Socialaccount] = list(Socialaccount.objects.all().only('user_id', 'extra_data'))

    # 부모댓글 작성자 프로필 사진 정보 추가 : picture
    user_id = [user.id for user in users if user.username == parent_comment.username][0]
    extra_data = [account.extra_data for account in socialaccounts if account.user_id == user_id][0]
    parent_comment.picture = json.loads(extra_data)['picture']

    # 부모댓글 관련 법규 정보 추가 : page_id, page_title
    page = Pages.objects.get(page_id=parent_comment.page_id)
    book_title = Books.objects.get(book_id=page.book_id).book_title
    parent_comment.page_title = "[" + str(book_title).replace(" ", "") + "] " + page.page_title
    parent_comment.page_id = page.page_id

    # 부모댓글 좋아요 관련 정보 추가 : is_liked, like_user_count
    like_parent_comment = list(parent_comment.like_users.all())
    if request.user in like_parent_comment:
        parent_comment.is_liked = "true"
    else:
        parent_comment.is_liked = "false"
    parent_comment.like_user_count = len(like_parent_comment)

    # 자식댓글 QuerySet
    sort = request.GET.get('sort', 'registered')  # 정렬기준 쿼리스트링을 가져온다, 없는 경우 default 최신순
    q = Q(parent_id=comment_id) & Q(rls_yn='Y') & (Q(status="C") | Q(status="U"))
    if sort == "popular":  # 인기순
        child_comments = Comments.objects.annotate(like_user_count=Coalesce(Subquery(
            UserLikeComment.objects.filter(comment_id=OuterRef('pk')).values('comment_id').annotate(
                count=Count('pk')).values('count')
        ), 0)).filter(q).order_by('-like_user_count', 'reg_dt')
    elif sort == "recent":  # 최신순
        child_comments = Comments.objects.filter(q).order_by('-reg_dt')
    else:  # 등록순
        child_comments = Comments.objects.filter(q).order_by('reg_dt')
    child_comments: List[Comments] = list(child_comments)

    for child_comment in child_comments:
        # 자식댓글 작성자 프로필 사진 정보 추가 : picture
        user_id = [user.id for user in users if user.username == child_comment.username][0]
        extra_data = [account.extra_data for account in socialaccounts if account.user_id == user_id][0]
        child_comment.picture = json.loads(extra_data)['picture']

        # 부모댓글 좋아요 관련 정보 추가 : is_liked, like_user_count
        like_child_comment = list(child_comment.like_users.all())
        if request.user in like_child_comment:
            child_comment.is_liked = "true"
        else:
            child_comment.is_liked = "false"
        if sort != "popular":
            child_comment.like_user_count = len(like_child_comment)

    # 페이징 처리
    if request.GET.get('page') is None:
        page = 1
    else:
        page = request.GET.get('page')
    paginator = Paginator(child_comments, 10).get_page(page)

    # 정렬기준 (템플릿에서 정렬기준을 selectbox 대신 div > a로 표현하기 위함)
    sort_list = [{'value': 'registered', 'label': '등록순'},
                 {'value': 'popular', 'label': '인기순'},
                 {'value': 'recent', 'label': '최신순'}]
    if sort != 'registered':
        for idx, item in enumerate(sort_list):
            if item.get('value') == sort:
                sel_item = sort_list[idx]
                sort_list.remove(sel_item)
                sort_list.insert(0, sel_item)

    context = {"parent_comment": parent_comment,
               "child_comments": paginator,
               "comments_count": str(len(child_comments)),
               "sort_list": sort_list,
               "child_view": child_view}

    # Cookie 생성 후 조회수 증감
    session_cookie = request.user
    cookie_name = F'comment_hits:{session_cookie}'
    target_comment = Comments.objects.get(comment_id=comment_id)
    response = render(request, "forum/forum_detail.html", context)

    if request.COOKIES.get(cookie_name) is not None:
        cookies = request.COOKIES.get(cookie_name)
        cookies_list = cookies.split('|')
        if str(comment_id) not in cookies_list:
            response.set_cookie(cookie_name, cookies + f'|{comment_id}', expires=None)
            target_comment.hit_count += 1
            target_comment.save()
            return response
    else:
        response.set_cookie(cookie_name, comment_id, expires=None)
        target_comment.hit_count += 1
        target_comment.save()
        return response

    return render(request, "forum/forum_detail.html", context)


# 댓글 좋아요 토글 function
@login_required(login_url="/account/google/login")
def like_comment(request, comment_id):
    # 댓글, 작성자 QuerySet 선언
    try:
        comment = Comments.objects.get(comment_id=comment_id)
        author = get_user_model().objects.get(username=comment.username)
    except Comments.DoesNotExist:
        return render(request, "404.html", {"message": "존재하지 않는 댓글입니다."})

    # 좋아요 삭제, 댓글 작성자 활동점수 -1
    if request.user in comment.like_users.all():
        comment.like_users.remove(request.user)
        result = "remove"
        if str(request.user) != comment.username:
            author.act_point = int(author.act_point) - 1
            author.save()
    # 좋아요 등록, 댓글 작성자 활동점수 +1
    else:
        comment.like_users.add(request.user)
        result = "add"
        if str(request.user) != comment.username:
            author.act_point = int(author.act_point) + 1
            author.save()
    return JsonResponse({"result": result})
