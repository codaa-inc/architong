import requests
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Books
from .models import Pages
from .forms import PostForm
from .forms import PageForm

from xml.etree import ElementTree

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

def viewBook(request, book_id) :
    book = Books.objects.filter(book_id=book_id)
    context = {'page': book}
    return render(request, 'viewer.html', context)

def viewPage(request, page_id) :
    # 해당 책의 페이지 호출
    page = Pages.objects.filter(page_id=page_id)
    print(page.query)
    context = {'page': page}
    return render(request, 'viewer.html', context)

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
    # 모델 객체 생성
    page = Pages()
    page.book_id = 1
    page.page_title = title
    page.wrt_dt = "2021-04-01 00:00"
    page.mdfcn_dt = "2021-04-01 00:00"
    if is_jomun == "조문":
        page.depth = 1
        # 부모ID로 depth가 0인 것 중의 가장 마지막 row의 page_id를 넣는다
        parent_id = Pages.objects.filter(depth=0).last().page_id
        page.parent_id = parent_id
        page.description = markdown_text
    else:
        page.depth = 0
        page.parent_id = 0
    page.save()     # 모델 DB 저장



# 마크다운 컨버팅 매서드 (조문단위)
def xml_to_markdown(xml_text):
    tree = ElementTree.fromstring(xml_text)
    jo_root = tree.iter(tag='조문단위')
    for jo in jo_root:  # 조 → H3
        global markdown_text
        global title
        global is_jomun
        if jo:
            is_jomun = jo.find('조문여부').text     # 조문 / 전문
            title = jo.find('조문내용').text.lstrip().rstrip().replace('(', ' ').split(')')[0]
            markdown_text = ""
            if is_jomun == "조문":
                header = jo.find('조문내용').text.lstrip().rstrip()
                if header.find(')') != -1:
                    markdown_text = "### " + header.split(")", 1)[0] + ")\n"
                    context = header.split(")", 1)[1].rstrip()
                    if context is not None:
                        markdown_text += context
                else:
                    markdown_text = header
                hang_root = jo.iter(tag='항')
                for hang in hang_root:
                    if hang:    # 항
                        markdown_text += hang.find('항내용').text.lstrip() + "\n"
                        ho_root = hang.iter(tag='호')
                        for idx, ho in enumerate(ho_root):
                            if ho:  # 호 → Pre
                                if idx == 0:
                                    markdown_text += "```" + "\n"
                                markdown_text += ho.find('호내용').text.lstrip() + "\n"
                                if idx == len(hang.findall('호')) - 1:
                                    markdown_text += "```" + "\n"
                            else:
                                break
                    else:
                        break
            insert_law(is_jomun, title, markdown_text)
        else:
            break
