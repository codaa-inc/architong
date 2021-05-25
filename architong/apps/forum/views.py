import json
import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.db.models import Subquery

from .models import Comments

@login_required
def comment(request, id):
    # 세션에서 사용자 아이디 추출
    username = request.user

    # GET 요청시 해당 페이지의 댓글 조회
    if request.method == 'GET':
        comments = []
        q = Q()
        q.add(Q(page_id=id), q.AND)
        q.add(~Q(status="D"), q.AND)
        q.add(Q(rls_yn="Y") | Q(rls_yn="N", username=username), q.AND)
        parent_node = Comments.objects.filter(Q(depth=0) & q).values()
        child_node = Comments.objects.filter(Q(depth=1) & q).values()
        # 부모 댓글 > 자식 댓글 : 계층형 데이터 정렬
        for parent in parent_node:
            if parent['status'] == "TD":
                parent['content'] = "이 댓글은 삭제되었습니다."
            comments.append(parent)
            childs = child_node.filter(parent_id=parent['comment_id'])
            for child in childs:
                comments.append(child)
        return HttpResponse(json.dumps(comments, cls=DjangoJSONEncoder), content_type="text/json")

    # POST 요청시 댓글 등록
    elif request.method == 'POST':
        nodestr = id.split('-')[0]
        idstr = id.split('-')[1]
        comment = Comments()
        comment.username = username
        comment.rls_yn = request.POST['rls_yn']
        comment.content = request.POST['content']
        comment.status = "C"
        if nodestr == 'parent':
            comment.depth = 0
            comment.parent_id = 0
            comment.page_id = idstr
        elif nodestr == 'child':
            comment.depth = 1
            comment.parent_id = idstr
            comment.page_id = Comments.objects.filter(comment_id=idstr).values('page_id')
        comment.save()
        # 저장한 comment 객체를 return
        comment_id = Comments.objects.order_by('-pk')[0].comment_id
        new_comment = Comments.objects.filter(comment_id=comment_id).values()
        new_comment = json.dumps(list(new_comment), cls=DjangoJSONEncoder)
        return HttpResponse(new_comment, content_type="text/json")

    # PUT 요청시 댓글 수정
    elif request.method == 'PUT':
        comment_id = id.split('-')[1]
        comment = Comments.objects.get(comment_id=comment_id)
        comment.content = request.PUT['content']
        comment.reg_dt = datetime.datetime.now()
        comment.status = "U"
        comment.save()
        # 저장한 comment 객체를 return
        new_comment = Comments.objects.filter(comment_id=comment_id).values()
        new_comment = json.dumps(list(new_comment), cls=DjangoJSONEncoder)
        return HttpResponse(new_comment, content_type="text/json")

    # DELETE 요청시 댓글 삭제
    elif request.method == 'DELETE':
        comment_id = id.split('-')[1]
        comment = Comments.objects.get(comment_id=comment_id)
        result = "delete"
        # 자식 댓글이 존재하는 경우 → 임시삭제 상태로 변경
        if comment.depth == 0:
            has_any_child = Comments.objects.filter(parent_id=comment_id, status="C").count()
            if has_any_child > 0:
                comment.status = "TD"
                comment.save()
                result = "temporary delete"
                return JsonResponse({"result": result})
        # 부모 댓글이 임시삭제 상태이면서 형제 댓글이 없을 때 → 부모 댓글을 삭제 상태로 변경
        elif comment.depth == 1:
            parent = Comments.objects.get(comment_id=comment.parent_id)
            sibling_count = Comments.objects.filter(parent_id=comment.parent_id, status="C").count()
            if parent.status == "TD" and sibling_count <= 1:
                parent.status = "D"
                parent.save()
                result = "parent delete"
        # 해당 댓글을 삭제 상태로 변경
        comment.status = "D"
        comment.save()
        return JsonResponse({"result": result})



