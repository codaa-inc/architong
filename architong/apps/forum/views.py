import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.db.models import Subquery
from .models import Comments

@login_required
def comment(request, id):
    # GET 요청시 해당 페이지의 댓글 조회 (계층형 데이터 정렬)
    if request.method == 'GET':
        comments = []
        parentNode = Comments.objects.filter(page_id=id, depth=0, rls_yn="Y").values()
        childNode = Comments.objects.filter(page_id=id, depth=1, rls_yn="Y").values()
        for parent in parentNode:
            comments.append(parent)
            childs = childNode.filter(parent_id=parent['comment_id'])
            for child in childs:
                comments.append(child)
        return HttpResponse(json.dumps(comments, cls=DjangoJSONEncoder), content_type="text/json")

    # POST 요청시 댓글 등록
    elif request.method == 'POST':
        nodestr = id.split('-')[0]
        idstr = id.split('-')[1]
        comment = Comments()
        comment.username = request.user
        comment.rls_yn = request.POST['rls_yn']
        comment.content = request.POST['content']
        if nodestr == 'parent':
            comment.depth = 0
            comment.parent_id = 0
            comment.page_id = idstr
        elif nodestr == 'child':
            comment.depth = 1
            comment.parent_id = idstr
            comment.page_id = Comments.objects.filter(comment_id=idstr).values('page_id')
        comment.save()
        new_comment = Comments.objects.filter(comment_id=Comments.objects.order_by('-pk')[0].comment_id).values()
        return HttpResponse(json.dumps(list(new_comment), cls=DjangoJSONEncoder), content_type="text/json")

