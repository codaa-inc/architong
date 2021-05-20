from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import HttpResponse
from .models import Comments

@login_required
def comment(request, page_id):
    # GET 요청시 해당 페이지의 댓글 조회
    if request.method == 'GET':
        comments = Comments.objects.filter(page_id=page_id, rls_yn="Y")
        return HttpResponse(serializers.serialize('json', comments), content_type="text/json-comment-filtered")
    # POST 요청시 댓글 등록
    elif request.method == 'POST':
        comment = Comments()
        comment.page_id = page_id
        comment.username = request.user
        comment.rls_yn = request.POST['rls_yn']
        comment.content = request.POST['content']
        comment.depth = 0
        comment.parent_id = 0
        comment.save()
        return HttpResponse({"result": "success"}, content_type="text/json-comment-filtered")

