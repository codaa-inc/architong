import requests
from django.shortcuts import render
from django.conf import settings
from xml.etree import ElementTree
from apps.book.models import Books
from apps.book.models import Pages

def index(request):
    books = Books.objects.all().order_by('book_title')
    context = {"books": books}
    return render(request, 'index.html', context)

'''
[ 법령 MST ] 
    - 216215 : 건축법
    - 228443 : 건축법 시행령
    - 228701 : 건축법 시행규칙
    - 217375 : 녹색건축물 조성 지원법
    - 223893 : 녹색건축물 조성 지원법 시행령
    - 224171 : 녹색건축물 조성 지원법 시행규칙
'''
def get_law(request):
    # Request : 국가법령정보 API call
    # Response : 법령 본문
    host = "http://www.law.go.kr/DRF/lawService.do?"
    OC = 'mediaquery1'
    target = 'law'  # 현행법령 본문 조항호목
    MST = '224171'
    type = 'XML'    # type : HTML / XML
    url = host + "OC=" + OC + "&target=" + target + "&MST=" + MST + "&type=" + type
    print(url)
    try:
        res = requests.get(url)
        if res.status_code == 200:
            xml_to_markdown_enforcement(res.text)
    except Exception as e:
        print(e)


def insert_law(is_jomun, title, markdown_text):
    page = Pages()  # 모델 객체 생성
    page.book_id = 6
    page.page_title = title
    page.description = markdown_text
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
법령 마크다운 디자인 적용
 - 전문 → H2 + 구분선
 - 조문 → H3
 - 항 → 디자인 없음
 - 호 → blockquote
'''
def xml_to_markdown_law(xml_text):
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

'''
시행령, 시행규칙 마크다운 디자인 적용
 - 전문 → H2 + 구분선
 - 조문 → H3
 - 항 → 디자인 없음
 - 호 → blockquote, ordered list 제거
 - 목 → dluble blockquote
 - 목 하위 텍스트(tab으로 구분) → triple blockquote
'''
def xml_to_markdown_enforcement(xml_text):
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
                                markdown_text += "> " + ho.find('호내용').text.lstrip().replace(". ", ".") + "\n"
                                if ho.find('목') != -1:
                                    mok_root = ho.iter(tag='목')
                                    for mok in mok_root:
                                        mok = mok.find('목내용').text.split('\t\t\t\t\t\t')
                                        for idx, row in enumerate(mok):
                                            if row:
                                                if idx == 0:
                                                    markdown_text += ">> " + row.lstrip() + '\n' + '\n'
                                                else:
                                                    markdown_text += ">>> " + row.lstrip() + '\n'
                                                if idx == len(mok) - 1:
                                                    markdown_text += '\n'
                                else:
                                    break
                            else:
                                break
                    else:
                        break
            else:                       # 전문 → H2 + 구분선
                markdown_text = "\n\n##" + title + "\n----------"
        insert_law(is_jomun, title, markdown_text)