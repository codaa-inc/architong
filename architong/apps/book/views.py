import requests

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.serializers import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from xml.etree import ElementTree

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
    books = Books.objects.filter(book_id=book_id)
    username = request.session.get('user')  # 세션으로부터 유저 정보 가져오기
    print("username : ", username)
    # 로그인된 사용자의 경우 페이지 정보에 북마크 등록여부 추가
    '''
    if username is not None:
        pages = Pages.objects.filter(book_id=book_id)
        print(pages.query)
    else:
        pages = Pages.objects.filter(book_id=book_id)
    '''
    pages = Pages.objects.filter(book_id=book_id)
    context = {'books': books, 'pages': pages}
    return render(request, 'viewer.html', context)


def view_page(request, page_id):
    '''
    if page_id is not None:
        pages = Pages.objects.filter(page_id=page_id) | Pages.objects.filter(parent_id=page_id)
        json_serializer = json.Serializer()
        context = {'pages': json_serializer.serialize(pages)}
        return JsonResponse(request, context)
'''

@login_required(login_url="/account/google/login")
def add_bookmark(request, page_id):
    if request.user.is_authenticated:
        bookmark = Bookmark()   # 모델 객체 생성
        bookmark.page_id = page_id
        bookmark.username = request.user
        bookmark.save()
        result = 'true'
    else:
        result = 'false'
    json_serializer = json.Serializer()
    context = {"result": json_serializer.serialize(result)}
    return JsonResponse(request, context)

def get_law(request):
    # Request : 국가법령정보 API call
    # Response : 법령 본문
    host = "http://www.law.go.kr/DRF/lawService.do?"
    OC = 'mediaquery1'
    target = 'law'  # 현행법령 본문 조항호목
    MST = '216215'  # 건축법
    type = 'XML'    # type : HTML / XML
    url = host + "OC=" + OC + "&target=" + target + "&MST=" + MST + "&type=" + type
    print(url)
    try:
        res = requests.get(url)
        if res.status_code == 200:
            xml_to_markdown(res.text)
    except Exception as e:
        print(e)


def insert_law(is_jomun, title, markdown_text):
    page = Pages() # 모델 객체 생성
    page.book_id = 1
    page.page_title = title
    page.description = markdown_text
    page.wrt_dt = "2021-04-01 00:00"
    page.mdfcn_dt = "2021-04-01 00:00"
    if is_jomun == "조문":
        page.depth = 1
        # 부모ID로 depth가 0인 것 중의 가장 마지막 row의 page_id를 넣는다
        parent_id = Pages.objects.filter(depth=0).last().page_id
        page.parent_id = parent_id
    else:
        page.depth = 0
        page.parent_id = 0
    page.save()     # 모델 DB 저장

'''
마크다운 디자인 적용
 - 전문 → H2 + 구분선
 - 조문 → H3
 - 항 → 디자인 없음
 - 호 → Blockquote
'''
def xml_to_markdown(xml_text):
    tree = ElementTree.fromstring(xml_text)
    jo_root = tree.iter(tag='조문단위')
    for jo in jo_root:  # 조문 → H3
        global markdown_text
        global title
        global is_jomun
        if jo:
            is_jomun = jo.find('조문여부').text
            title = jo.find('조문내용').text.lstrip().rstrip().replace('(', ' ').split(')')[0]
            if is_jomun == "조문":        # 조문 → H3
                header = jo.find('조문내용').text.lstrip().rstrip()
                if header.find(')') != -1:
                    markdown_text = "### " + header.split(")", 1)[0] + ")\n"
                    context = header.split(")", 1)[1]
                    if context is not None:
                        markdown_text += context.rstrip() + "\n"
                else:
                    markdown_text = header
                hang_root = jo.iter(tag='항')
                for hang in hang_root:   # 항 → 디자인 없음
                    if hang:
                        if hang.find('항내용') is not None:
                            markdown_text += hang.find('항내용').text.lstrip() + "\n"
                        ho_root = hang.iter(tag='호')
                        for idx, ho in enumerate(ho_root):
                            if ho:        # 호 → Blockquote
                                markdown_text += ">" + ho.find('호내용').text.lstrip() + "\n"
                            else:
                                break
                    else:
                        break
            else:                       # 전문 → H2 + 구분선
                markdown_text = "\n\n##" + title + "\n----------"
        insert_law(is_jomun, title, markdown_text)

