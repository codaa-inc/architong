from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import HttpResponse
from .models import Comments

@login_required
def comment(request, id):
    # GET 요청시 해당 페이지의 댓글 조회
    if request.method == 'GET':
        comments = Comments.objects.filter(page_id=id, rls_yn="Y")
        return HttpResponse(serializers.serialize('json', comments), content_type="text/json")
    # POST 요청시 댓글 등록
    elif request.method == 'POST':
        idstr = id.split('-')[1]
        comment = Comments()
        comment.username = request.user
        comment.rls_yn = request.POST['rls_yn']
        comment.content = request.POST['content']
        if id.find('parent'):
            comment.depth = 0
            comment.parent_id = 0
            comment.page_id = idstr
        elif id.find('child'):
            page_id = Comments.objects.get(comment_id=idstr).only('page_id')
            comment.depth = 1
            comment.parent_id = idstr
            comment.page_id = page_id

        # TODO : apps.forum.models.Comments.DoesNotExist: Comments matching query does not exist.

        comment.save()
        return HttpResponse({"result": "success"}, content_type="text/json")

