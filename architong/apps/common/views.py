import requests
import json

from django.shortcuts import render
from django.conf import settings
from xml.etree import ElementTree
from django.views import View
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q

from apps.book.models import Books, Bookmark, Pages
from apps.forum.models import Comments
from .models import AuthUser
from .models import SocialaccountSocialaccount as Socialaccount


# 메인 페이지 조회 / 문서 검색 function
def index(request):
    books = Books.objects.all().order_by('book_title')  # 전체 쿼리셋
    # GET 요청일때 전체 쿼리셋을 가져온다
    if request.method == 'GET':
        page = request.GET.get('page')  # 이동할 페이지
        paginator = Paginator(books, 6).get_page(page)
        return render(request, 'index.html', {"books": paginator})

    # POST 요청일때 해당 검색조건을 적용한 쿼리셋을 가져온다.
    elif request.method == 'POST':
        text = request.POST['search-box']           # 검색어
        option = request.POST['search-option']      # 검색 범위 옵션
        page = request.POST['page']                 # 이동할 페이지
        if option == '0':
            books = books.filter(book_title__icontains=text)
        elif option == '1':
            page = Pages.objects.all().filter(description__icontains=text).only('book_id')
            book_id_list = page.values_list('book_id', flat=True).distinct().order_by("book_id")
            books = books.filter(book_id__in=book_id_list)
        elif option == '2':
            books = books.filter(author_id__icontains=text)
        paginator = Paginator(books, 6).get_page(page)
        return render(request, 'index.html', {"books": paginator, "search_term": text})


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
        return render(request, "bookmark.html", {"bookmarks": bookmarks})


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


# 유저 프로필 페이지 function
@login_required(login_url="/account/google/login")
def profile(request):
    if request.method == 'GET':
        status = Q(status="C") | Q(status="U")
        comment_count = Comments.objects.filter(Q(username=request.user) & status).count()
        context = {"comment_count": str(comment_count)}
        return render(request, "profile.html", context)


# 법규 데이터를 처리하는 class
class LawView(View):
    '''
    [ 법령 MST ]
        - 216215 : 건축법
        - 228443 : 건축법 시행령
        - 228701 : 건축법 시행규칙
        - 217375 : 녹색건축물 조성 지원법
        - 223893 : 녹색건축물 조성 지원법 시행령
        - 224171 : 녹색건축물 조성 지원법 시행규칙

    [ 별표/서식 ]
        - target : licby
        - search : 2
        - query : 건축법 시행령 / 건축법 시행규칙 / 녹색건축물 조성 지원법 시행령 / 녹색건축물 조성 지원법 시행규칙
        - full url : http://www.law.go.kr/DRF/lawSearch.do?OC=mediaquery1&target=licbyl&type=XML&search=2&query=
    '''
    # 법규 API 호출 function
    def get(self, request):
        # Request : 국가법령정보 API call
        # Response : 법령 본문
        host = "http://www.law.go.kr/DRF/lawService.do?"
        OC = 'mediaquery1'
        target = 'law'  # 현행법령 본문 조항호목
        MST = '224171'
        type = 'XML'    # type : HTML / XML
        url = host + "OC=" + OC + "&target=" + target + "&MST=" + MST + "&type=" + type
        try:
            res = requests.get(url)
            print(res.url)
            if res.status_code == 200:
                self.xml_to_markdown_attachments(res.text)
        except Exception as e:
            print(e)

    '''
    법령 마크다운 디자인 적용
     - 전문 → H2 + 구분선
     - 조문 → H3
     - 항 → 디자인 없음
     - 호 → blockquote
    '''
    # 일반법 → 마크다운 파싱 function
    def xml_to_markdown_law(self, xml_text):
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
            self.insert_law(is_jomun, title, markdown_text)

    '''
    시행령, 시행규칙 마크다운 디자인 적용
     - 전문 → H2 + 구분선
     - 조문 → H3
     - 항 → 디자인 없음
     - 호 → blockquote, ordered list 제거
     - 목 → dluble blockquote
     - 목 하위 텍스트(tab으로 구분) → triple blockquote
    '''
    # 시행령, 시행규칙 → 마크다운 파싱 function
    def xml_to_markdown_enforcement(self, xml_text):
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
            self.insert_law(is_jomun, title, markdown_text)

    '''
    별표/서식 마크다운 디자인 적용
     - 별표제목 → 별표제목 + &nbsp;&nbsp;&nbsp;&nbsp; + 파일링크
     - 별표서식파일링크, 별표서식PDF파일링크 → 이미지링크
        [![]({% static 'img/custom/hg_download.png' %})](http://www.law.go.kr + 링크)
        [![]({% static 'img/custom/pdf_download.png' %})](http://www.law.go.kr + 링크)
    '''
    # 별표/서식 → 마크다운 파싱 function
    def xml_to_markdown_attachments(self, xml_text):
        global order_branch
        tree = ElementTree.fromstring(xml_text)
        attachments = tree.iter(tag='별표단위')
        for attachment in attachments:  # 조문 → H3
            attachment_gb = attachment.find('별표구분').text
            order = str(int(attachment.find('별표번호').text))
            order_branch = str(int(attachment.find('별표가지번호').text))

            if attachment_gb == "별표":
                if order_branch != "0":
                    order += "의" + order_branch
                order = "별표 " + order
            elif attachment_gb == "서식":
                if order_branch != "0":
                    order += "호의" + order_branch
                else:
                    order += "호"
                order = "별지 제" + order + "서식"

            title = "[" + order + "] " + attachment.find('별표제목').text.replace("&lt;", "<").replace("&gt;", ">")
            hwp = "[![](https://www.law.go.kr/LSW/images/button/btn_han.gif)](http://www.law.go.kr" + attachment.find("별표서식파일링크").text + ")"
            pdf = "[![](https://www.law.go.kr/LSW/images/button/btn_pdf.gif)](http://www.law.go.kr" + attachment.find("별표서식PDF파일링크").text + ")"
            markdown_text = title + "&nbsp;&nbsp;&nbsp;&nbsp;" + hwp + "&nbsp;&nbsp;" + pdf + "\n"
            self.insert_law("별표", title, markdown_text)

    # 법규 마크다운 저장 function
    def insert_law(is_jomun, title, markdown_text):
        page = Pages()  # 모델 객체 생성
        page.book_id = 6
        page.page_title = title
        page.description = markdown_text

        if is_jomun == "조문" or is_jomun == "별표":
            page.depth = 1
            # 부모ID로 depth가 0인 것 중의 가장 마지막 row의 page_id를 넣는다
            # parent_id = Pages.objects.filter(depth=0).last().page_id
            page.parent_id = 594
        else:
            page.depth = 0
            page.parent_id = 0
        page.save()  # 모델 DB 저장
