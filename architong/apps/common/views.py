import requests
import json

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from xml.etree import ElementTree

from django.views import View
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q

from apps.common.models import SocialaccountSocialaccount as Socialaccount
from apps.book.models import Books, Bookmark, Pages
from apps.forum.models import Comments, UserLikeComment


# 메인 페이지 조회 / 문서 검색 function
def index(request):
    books = Books.objects.filter(codes_yn="Y").order_by('-wrt_dt')  # 전체 쿼리셋
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
def profile(request, username):
    if request.method == 'GET':
        # 사용자정보, 활동점수, 댓글수, 작성한 댓글의 좋아요 합계 QuerySet
        user_info = get_user_model().objects.get(username=username)
        user_info.picture = json.loads(Socialaccount.objects.get(user_id=user_info.id).extra_data)['picture']
        act_point = get_user_model().objects.get(username=username).act_point

        # 최근활동 QuerySet
        comments = Comments.objects.filter(Q(username=username) & (Q(status="C") | Q(status="U"))).order_by('-reg_dt')
        like_count = 0
        for comment in comments:
            like_count += comment.like_users.all().count()

        # 최근활동 페이징 처리
        page = request.GET.get('page')
        paginator = Paginator(comments, 10).get_page(page)

        context = {"user_info": user_info,
                   "act_point": str(act_point),
                   "comment_count": str(comments.count()),
                   "like_count": str(like_count),
                   "comments": paginator}
        return render(request, "profile.html", context)


# 법규 데이터를 처리하는 class
class LawView(View):
    # 관리자 법규등록 페이지 렌더링 function
    def get(self, request):
        if request.user.is_staff:
            return render(request, "law_add.html")

    # 법규 API 호출 function
    def post(self, request):
        if request.user.is_staff:
            host = "http://www.law.go.kr/DRF/lawService.do?"
            OC = 'mediaquery1'
            type = 'XML'
            target = request.POST['target']
            url = host + "OC=" + OC + "&target=" + target + "&type=" + type
            if target == 'law' or target == 'ordin':        # 일반법, 자치법규
                url += "&MST=" + request.POST['target_no']
            elif target == 'admrul':                        # 행정규칙
                url += "&LID=" + request.POST['target_no']
            try:
                res = requests.get(url)
                print("request url : ", res.url)
                if res.status_code == 200:
                    xml_text = ElementTree.fromstring(res.text)
                    html_url = str(res.url.replace("XML", "HTML"))
                    book_title = xml_text.find('기본정보').find('법령명_한글').text
                    book_count = Books.objects.filter(book_title=book_title).count()
                    # 이미 등록되어있는지 중복체크
                    if book_count < 1:
                        book = Books()
                        book.book_title = book_title
                        book.enfc_dt = xml_text.find('기본정보').find('시행일자').text
                        book.author_id = request.user.username
                        book.codes_yn = "Y"
                        book.rls_yn = "Y"
                        # 법규정보 Books 테이블 등록
                        book.create()
                        book_id = Books.objects.last().book_id
                        # 마크다운 파싱
                        self.xml_to_markdown_law(xml_text, book_id)
                        return JsonResponse({"result": "success", "book_id": book_id, "html_url": html_url})
                    else:
                        return JsonResponse({"result": "exist", "message": "이미 등록된 법규입니다."})
            except Exception as e:
                return JsonResponse({"result": "fail", "html_url": html_url})


    '''
    [ 법령(일반법, 시행령, 시행규칙) 마크다운 디자인 ]
     - 전문 → H2 + 구분선
     - 조문 → H3
     - 항 → 디자인 없음
     - 호 → blockquote, ordered list 제거
     - 목 → dluble blockquote
     - 목 하위 텍스트(tab으로 구분) → triple blockquote
     - 이미지 → 이미지링크
     - 별표제목 → 별표제목 + 파일링크
     - 별표서식파일링크, 별표서식PDF파일링크 → 이미지링크
    '''
    # 시행령, 시행규칙 → 마크다운 파싱 function
    def xml_to_markdown_law(self, xml_text, book_id):
        # 조문 컨버팅
        jo_root = xml_text.iter(tag='조문단위')
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
                self.insert_page(is_jomun, title, self.get_img_link(markdown_text), book_id)

        # 별표, 서식 컨버팅
        attachments_root = xml_text.iter(tag='별표단위')
        if attachments_root:
            for attachment in attachments_root:
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
                title = "[" + order + "] " \
                        + attachment.find('별표제목').text.replace("&lt;", "<").replace("&gt;", ">")
                hwp = "[![](https://www.law.go.kr/LSW/images/button/btn_han.gif)](http://www.law.go.kr" \
                      + attachment.find("별표서식파일링크").text + ")"
                pdf = "[![](https://www.law.go.kr/LSW/images/button/btn_pdf.gif)](http://www.law.go.kr" \
                      + attachment.find("별표서식PDF파일링크").text + ")"
                markdown_text = title + "&nbsp;&nbsp;&nbsp;&nbsp;" + hwp + "&nbsp;&nbsp;" + pdf + "\n"
                self.insert_page("별표", title, markdown_text, book_id)

    # 이미지 링크 처리
    def get_img_link(self, context):
        img_start_tag = '<img id="'
        img_end_tag = '"></img>'
        if img_start_tag in context:
            if img_end_tag in context:
                return context\
                    .replace(img_start_tag, "\n![](https://www.law.go.kr/LSW/flDownload.do?flSeq=")\
                    .replace(img_end_tag, ")\n")
        else:
            return context

    # 법규 마크다운 저장 function
    def insert_page(self, is_jomun, title, markdown_text, book_id):
        page = Pages()
        page.book_id = book_id
        page.page_title = title
        page.description = markdown_text
        if is_jomun == "조문":
            page.depth = 1
            parent_queryset = Pages.objects.filter(book_id=book_id, depth=0).last()
            # 부모 id로 가장 최근의 depth=0인 페이지의 id를 넣는다
            if parent_queryset:
                page.parent_id = parent_queryset.page_id
            # 전문(장)없이 조문(조)로만 구성된 경우, 부모레벨을 제목페이지를 생성하고 그 id를 부모 id로 넣는다.
            else:
                page_parent = Pages()
                page_parent.book_id = book_id
                book_title = Books.objects.get(book_id=book_id).book_title
                page_parent.page_title = book_title
                page_parent.description = "\n\n##" + book_title + "\n----------"
                page_parent.depth = 0
                page_parent.parent_id = 0
                page_parent.save()
                page.parent_id = Pages.objects.filter(book_id=book_id, depth=0).last().page_id
        elif is_jomun == "별표":
            page.depth = 1
            attachment_queryset = Pages.objects.filter(book_id=book_id, depth=0, page_title="별표/서식").last()
            # 첫번째 별표/서식 등록시 부모레벨 생성
            if attachment_queryset:
                page.parent_id = attachment_queryset.page_id
            else:
                page_attachment = Pages()
                page_attachment.book_id = book_id
                page_attachment.page_title = "별표/서식"
                page_attachment.description = "\n\n##별표/서식\n----------"
                page_attachment.depth = 0
                page_attachment.parent_id = 0
                page_attachment.save()
                page.parent_id = Pages.objects.filter(book_id=book_id, depth=0).last().page_id
        else:
            page.depth = 0
            page.parent_id = 0
        page.save()  # 모델 DB 저장


# 법규관리 페이지를 렌더링 하는 function
@staff_member_required
def manage_law(request):
    context = {"books": Books.objects.filter(codes_yn="Y")}
    return render(request, "law_admin.html", context)


# 회원관리 페이지를 렌더링 하는 function
@staff_member_required
def manage_user(request):
    context = {"users": get_user_model().objects.all()}
    return render(request, "user_admin.html", context)
