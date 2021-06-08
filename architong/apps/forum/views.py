import json
import datetime
from typing import List

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator
from django.db.models import Q, Subquery
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse
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

        # 부모,자식 댓글 QuerySet
        q = Q(page_id=id) & ~Q(status="D")
        if username is not None:
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
        username = request.user
        if username.is_authenticated:
            # Comment 객체 선언, ID 지정
            comment = Comments()
            nodestr = id.split('-')[0]
            idstr = id.split('-')[1]

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

            # 좋아요 관련 정보 추가 : is_liked, like_user_count
            for new_comment in new_comment_obj:
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
            message = "로그인이 필요한 서비스입니다.\n로그인하시겠습니까?"
            context = {"result": "fail", "message": message}
            return JsonResponse(context, content_type="text/json")

    # DELETE 요청시 댓글 삭제
    def delete(self, request, id):
        username = request.user
        if username.is_authenticated:
            comment_id = id.split('-')[1]
            comment = Comments.objects.get(comment_id=comment_id)
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
            context = {"result": "fail"}
            return JsonResponse(context, content_type="text/json")


# 댓글 수정 function
@login_required
def comment_update(request, id):
    if request.method == 'POST':
        # Comment 객체 선언, ID 지정
        comment_id = id.split('-')[1]
        comment = Comments.objects.get(comment_id=comment_id)

        # 댓글을 수정한다.
        comment.content = request.POST['content']
        comment.reg_dt = datetime.datetime.now()
        comment.status = "U"
        comment.save()

        # 저장한 comment 객체를 return 한다.
        update_comment_obj = Comments.objects.filter(comment_id=comment_id).values()

        # 좋아요 관련 정보 추가 : is_liked, like_user_count
        for update_comment in update_comment_obj:
            like_comment = Comments.objects.get(comment_id=comment_id).like_users.all()
            if request.user in like_comment:
                update_comment['is_liked'] = "true"
            else:
                update_comment['is_liked'] = "false"
            update_comment['like_user_count'] = len(like_comment)

        update_comment = json.dumps(update_comment, cls=DjangoJSONEncoder)
        return HttpResponse(update_comment, content_type="text/json")


# 포럼 리스트 조회 function
def forum(request):
    # 쿼리셋 호출
    books: List[Books] = list(Books.objects.all().only('book_id', 'book_title'))
    pages: List[Pages] = list(Pages.objects.all())
    q = Q(depth=0) & Q(rls_yn='Y') & (Q(status="C") | Q(status="U"))
    comments: List[Comments] = list(Comments.objects.filter(q).order_by('-reg_dt'))
    child_comments: List[Comments] = list(Comments.objects.filter(depth=1, rls_yn='Y'))
    socialaccount: List[Socialaccount] = list(Socialaccount.objects.all().only('user_id', 'extra_data'))

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
        comment.like_user_count = len(like_comment)

        # 자식댓글 갯수 추가
        child_count = [child for child in child_comments if child.parent_id == comment.comment_id]
        comment.child_count = len(child_count)

    # 페이징 처리
    if request.GET.get('page') is None:
        page = 1
    else:
        page = request.GET.get('page')
    paginator = Paginator(comments, 10).get_page(page)

    context = {"comments": paginator,
               "comments_count": str(len(comments))}
    return render(request, 'forum.html', context)


# 포럼 상세 조회 function
def forum_detail(request, comment_id):
    # 부모,자식 공통 QuerySet 호출
    socialaccounts: List[Socialaccount] = list(Socialaccount.objects.all().only('user_id', 'extra_data'))
    users = list(get_user_model().objects.all().only('id', 'username'))

    # 부모댓글 QuerySet
    parent_comment = Comments.objects.get(comment_id=comment_id)

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
    q = Q(parent_id=comment_id) & Q(rls_yn='Y') & (Q(status="C") | Q(status="U"))
    child_comments: List[Comments] = list(Comments.objects.filter(q))

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
        child_comment.like_user_count = len(like_child_comment)

    # 페이징 처리
    if request.GET.get('page') is None:
        page = 1
    else:
        page = request.GET.get('page')
    paginator = Paginator(child_comments, 10).get_page(page)

    context = {"parent_comment": parent_comment,
               "child_comments": paginator,
               "comments_count": str(len(child_comments))}
    return render(request, "forum_detail.html", context)


# 댓글 좋아요 토글 function
@login_required
def like_comment(request, comment_id):
    # 댓글, 작성자 QuerySet 선언
    comment = Comments.objects.get(comment_id=comment_id)
    author = get_user_model().objects.get(username=comment.username)

    # 좋아요 삭제, 댓글 작성자 활동점수 -1
    if request.user in comment.like_users.all():
        comment.like_users.remove(request.user)
        author.act_point = int(author.act_point) - 1
        author.save()
        result = "remove"

    # 좋아요 등록, 댓글 작성자 활동점수 +1
    else:
        comment.like_users.add(request.user)
        author.act_point = int(author.act_point) + 1
        author.save()
        result = "add"
    return JsonResponse({"result": result})
