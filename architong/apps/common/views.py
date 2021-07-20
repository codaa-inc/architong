import requests
import json
import datetime

from datetime import datetime, timedelta, timezone
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from xml.etree import ElementTree

from django.views import View
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q

from apps.common.models import SocialaccountSocialaccount as Socialaccount
from apps.book.models import Books, Bookmark, Pages, UserLikeBook
from apps.forum.models import Comments, UserLikeComment


# 메인 페이지 조회 / 문서 검색 function
def index(request):
    books = Books.objects.filter(rls_yn="Y").order_by('-hit_count')  # 전체 쿼리셋, default 조회순 정렬
    # 검색조건 콤보박스
    sort_list = [{'value': '0', 'label': '제목'},
                 {'value': '1', 'label': '내용'},
                 {'value': '2', 'label': '저자명'}]

    # GET 요청일때 전체 쿼리셋을 가져온다
    if request.method == 'GET':
        # 작성자가 일반회원인 경우에만 소셜계정 프로필 출력, 관리자는 기본이미지를 출력함
        for book in books:
            user_info = get_user_model().objects.get(username=book.author_id)
            if user_info.is_staff == 0:
                book.picture = json.loads(Socialaccount.objects.get(user_id=user_info.id).extra_data)['picture']
        # 페이징처리
        page = request.GET.get('page')
        paginator = Paginator(books, 6).get_page(page)
        context = {"books": paginator,
                   "sort_list": sort_list}
        return render(request, 'common/index.html', context)

    # POST 요청일때 해당 검색조건을 적용한 쿼리셋을 가져온다.
    elif request.method == 'POST':
        text = request.POST['search-box']           # 검색어
        option = request.POST['search-option']      # 검색 범위 옵션
        page = request.POST['page']                 # 이동할 페이지

        # 검색조건에 따른 filter 적용
        if option == '0':
            books = books.filter(book_title__icontains=text)
        elif option == '1':
            page = Pages.objects.all().filter(description__icontains=text).only('book_id')
            book_id_list = page.values_list('book_id', flat=True).distinct().order_by("book_id")
            books = books.filter(book_id__in=book_id_list)
            for idx, item in enumerate(sort_list):
                if item.get('value') == option:
                    sel_item = sort_list[idx]
                    sort_list.remove(sel_item)
                    sort_list.insert(0, sel_item)
        elif option == '2':
            books = books.filter(author_id__icontains=text)
            for idx, item in enumerate(sort_list):
                if item.get('value') == option:
                    sel_item = sort_list[idx]
                    sort_list.remove(sel_item)
                    sort_list.insert(0, sel_item)
        paginator = Paginator(books, 6).get_page(page)
        context = {"books": paginator,
                   "search_term": text,
                   "sort_list": sort_list}
        return render(request, 'common/index.html', context)


# 유저 프로필 페이지 function
class Profile(View):
    def get(self, request, username):
        # 사용자정보, 활동점수, 댓글수, 작성한 댓글의 좋아요 합계 QuerySet
        user_info = get_user_model().objects.get(username=username)
        user_info.picture = json.loads(Socialaccount.objects.get(user_id=user_info.id).extra_data)['picture']
        act_point = get_user_model().objects.get(username=username).act_point

        # 최근활동, 알림 QuerySet 선언
        recent_act_list = []
        noti_list = []
        profile = Profile()

        # 최근활동 - 댓글, 댓글 좋아요
        like_count = 0
        comments = Comments.objects.filter(Q(username=username) & (Q(status="C") | Q(status="U")))
        for comment in comments:
            like_users = UserLikeComment.objects.filter(comment_id=comment.comment_id)
            like_count += like_users.count()
            for like_user in like_users:
                target_user = get_user_model().objects.get(id=like_user.user_id).username
                # 알림 - 내 댓글에 좋아요 누른 기록 보임
                if username == str(request.user) and comment.username != target_user:
                    noti_list.append({'flag': "like_comment", 'content_id': comment.comment_id,
                                      'content': comment.content, 'act_dt': like_user.reg_dt,
                                      'target_user': target_user})
            recent_act_list.append({'flag': "comment", 'content_id': comment.comment_id,
                                    'content': comment.content, 'act_dt': comment.reg_dt})

        # 최근활동 - 위키, 위키 좋아요
        wiki_list = Books.objects.filter(author_id=username, codes_yn="N", rls_yn="Y")
        for wiki in wiki_list:
            like_users = UserLikeBook.objects.filter(book=wiki.book_id)
            for like_user in like_users:
                target_user = get_user_model().objects.get(id=like_user.user_id).username
                # 알림 - 내 위키에 좋아요 누른 기록 보임
                if username == str(request.user) and wiki.author_id != target_user:
                    noti_list.append({'flag': "like_wiki", 'content_id': wiki.book_id, 'content': wiki.book_title,
                                      'act_dt': like_user.reg_dt, 'target_user': target_user})
            recent_act_list.append({'flag': "wiki", 'content_id': wiki.book_id,
                                    'content': wiki.book_title, 'act_dt': wiki.mdfcn_dt})

        # 알림 - 나의 위키 또는 댓글에 리플
        if username == str(request.user):
            page_list = Pages.objects.filter(book_id__in=wiki_list.values_list('book_id')).values_list('page_id')
            comment_list = Comments.objects.filter(
                Q(parent_id__in=comments.values_list('page_id')) | Q(page_id__in=page_list)
                & ~Q(username=username)).order_by('page_id').distinct()
            for comment in comment_list:
                noti_list.append({"flag": "reply", "content_id": comment.comment_id, "content": comment.content,
                                  "act_dt": comment.reg_dt, "target_user": comment.username})

        # 최근활동 리스트 - 날짜별 정렬, 날짜 포맷팅, 페이징 처리
        sorted_recent_act_list = sorted(recent_act_list, key=(lambda x: x['act_dt']))
        for sorted_recent_act in sorted_recent_act_list:
            sorted_recent_act['act_dt'] = profile.act_dt_string(sorted_recent_act['act_dt'])
        sorted_recent_act_list.reverse()
        page = request.GET.get('page')
        paginator = Paginator(sorted_recent_act_list, 5).get_page(page)
        context = {"user_info": user_info,
                   "act_point": str(act_point),
                   "comment_count": str(comments.count()),
                   "like_count": str(like_count),
                   "recent_act_list": paginator}

        # 알림 리스트 - 날짜별 정렬, 날짜 포맷팅, 페이징 처리
        if username == str(request.user):
            sorted_noti_list = sorted(noti_list, key=(lambda x: x['act_dt']))
            for sorted_noti in sorted_noti_list:
                sorted_noti['act_dt'] = profile.act_dt_string(sorted_noti['act_dt'])
            sorted_noti_list.reverse()
            noti_page = request.GET.get('noti')
            noti_paginator = Paginator(sorted_noti_list, 5).get_page(noti_page)
            context["noti_list"] = noti_paginator
        return render(request, "common/profile.html", context)

    @staticmethod
    def act_dt_string(act_dt):
        time = datetime.now() - act_dt
        if time < timedelta(minutes=1):
            return '방금 전'
        elif time < timedelta(hours=1):
            return str(int(time.seconds / 60)) + '분 전'
        elif time < timedelta(days=1):
            return str(int(time.seconds / 3600)) + '시간 전'
        elif time < timedelta(days=7):
            time = datetime.now(tz=timezone.utc).date() - act_dt.date()
            return str(time.days) + '일 전'
        else:
            return act_dt


# 법규 데이터를 처리하는 class
class LawView(View):
    # 법규 API 호출 function
    def post(self, request):
        if request.user.is_staff:       # 관리자 권한 검사
            host = "http://www.law.go.kr/DRF/lawService.do?"
            OC = json.loads(open('././config/keys/secret_key.json', 'r').read())['OC']
            type = 'XML'
            url = host + "OC=" + OC + "&type=" + type
            target_sel = request.POST['target']
            if target_sel == "0":           # 법령
                url += "&target=law&MST=" + request.POST['target_no']
            elif target_sel == "1":         # 행정규칙
                url += "&target=admrul&LID=" + request.POST['target_no']
            elif target_sel == "2":         # 자치법규
                url += "&target=ordin&MST=" + request.POST['target_no']
            try:
                res = requests.get(url)
                print("request url : ", res.url)
                if res.status_code == 200:
                    xml_text = ElementTree.fromstring(res.text)
                    html_url = str(res.url.replace("XML", "HTML"))
                    if target_sel == "0":  # 법령
                        book_title = xml_text.find('기본정보').find('법령명_한글').text
                    elif target_sel == "1":  # 행정규칙
                        book_title = xml_text.find('행정규칙기본정보').find('행정규칙명').text
                    elif target_sel == "2":  # 자치법규
                        book_title = xml_text.find('자치법규기본정보').find('자치법규명').text
                    book_count = Books.objects.filter(book_title=book_title).count()
                    # 이미 등록되어있는지 중복체크
                    if book_count == 0:
                        username = request.user
                        # 마크다운 파싱
                        if target_sel == "0":  # 법령
                            self.xml_to_markdown_law(xml_text, username, target_sel)
                        elif target_sel == "1":  # 행정규칙
                            self.xml_to_markdown_admrul(xml_text, username, target_sel)
                        elif target_sel == "2":  # 자치법규
                            self.xml_to_markdown_ordin(xml_text, username, target_sel)
                        return JsonResponse({"result": "success", "html_url": html_url, "message": "등록 되었습니다."})
                    else:
                        return JsonResponse({"result": "exist", "message": "이미 등록된 법규입니다."})
                else:
                    return JsonResponse({"result": "fail", "message": "API 응답없음"})
            except Exception as e:
                return JsonResponse({"result": "fail", "html_url": html_url,  "message": "API 구문오류"})
        else:
            return JsonResponse({"result": "forbidden", "message": "잘못된 접근입니다."})


    '''
    [ 법령 마크다운 디자인 ]
     - 전문 → H2 + 구분선
     - 조문 → H3
     - 항 → 디자인 없음
     - 호 → blockquote, ordered list 제거
     - 목 → blockquote * 2
     - 목 하위 텍스트(tab으로 구분) → blockquote * 3
     - 이미지 → 이미지링크
     - 별표제목 → 별표제목 + 파일링크
     - 별표서식파일링크, 별표서식PDF파일링크 → 이미지링크
    '''
    def xml_to_markdown_law(self, xml_text, username, target_sel):
        law = []
        # 조문 컨버팅
        jo_root = xml_text.iter(tag='조문단위')
        for idx, jo in enumerate(jo_root):  # 조문 → H3
            is_jomun = jo.find('조문여부').text
            title = jo.find('조문내용').text.lstrip().rstrip().replace('(', ' ').split(')')[0]
            # 전문(장)없이 조문(조)로만 구성된 경우, 부모레벨을 제목페이지를 생성
            if idx == 0 and (is_jomun == "조문" or is_jomun == "Y"):
                law.append({"page_title": title, "description": "\n\n##" + title + "\n----------", "depth": 0})
            # 조문 → H3
            if is_jomun == "조문":
                header = jo.find('조문내용').text.lstrip().rstrip()
                if header.find(')') != -1:
                    markdown_text = "### " + header.split(")", 1)[0] + ")\n"
                    context = header.split(")", 1)[1]
                    if context is not None:
                        markdown_text += context.rstrip() + "\n"
                else:
                    markdown_text = header
                hang_root = jo.iter(tag='항')
                # 항 → 디자인 없음
                for hang in hang_root:
                    if hang:
                        if hang.find('항내용') is not None:
                            markdown_text += hang.find('항내용').text.lstrip() + "\n"
                        ho_root = hang.iter(tag='호')
                        # 호 → Blockquote
                        for idx, ho in enumerate(ho_root):
                            if ho:
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
                depth = 1
            # 전문 → H2 + 구분선
            else:
                markdown_text = "\n\n##" + title + "\n----------"
                if "절" in title.split(" ")[0]:
                    title = "null"
                    depth = 1
                else:
                    depth = 0
            law.append({"page_title": title,
                        "description": self.get_img_link(markdown_text),
                        "depth": depth})

        # 별표, 서식 컨버팅
        attachments_root = xml_text.iter(tag='별표단위')
        if attachments_root:
            for idx, attachment in enumerate(attachments_root):
                # 첫번째 별표/서식 등록시 부모레벨 생성
                if idx == 0:
                    law.append({"page_title": "별표/서식",
                                "description": "\n\n##별표/서식\n----------",
                                "depth": 0})
                attachment_gb = attachment.find('별표구분').text
                order = "" if int(attachment.find('별표번호').text) == 0 else str(int(attachment.find('별표번호').text))
                order_branch = str(int(attachment.find('별표가지번호').text))
                if attachment_gb == "별표":
                    if order_branch != "0":
                        order += "의" + order_branch
                    if order == "":
                        order = "별표" + order
                    else:
                        order = "별표 " + order
                elif attachment_gb == "서식":
                    if order_branch != "0":
                        order += "호의" + order_branch
                    else:
                        order += "호"
                    order = "별지 제" + order + "서식"
                title = "[" + order + "] " + attachment.find('별표제목').text.replace("&lt;", "<").replace("&gt;", ">")
                markdown_text = title
                if attachment.find("별표서식파일링크") is not None:
                    hwp = "[![](https://www.law.go.kr/LSW/images/button/btn_han.gif)](http://www.law.go.kr" \
                          + attachment.find("별표서식파일링크").text + ")"
                    markdown_text += "&nbsp;&nbsp;&nbsp;&nbsp;" + hwp
                if attachment.find("별표서식PDF파일링크") is not None:
                    pdf = "[![](https://www.law.go.kr/LSW/images/button/btn_pdf.gif)](http://www.law.go.kr" \
                          + attachment.find("별표서식PDF파일링크").text + ")"
                    markdown_text += "&nbsp;&nbsp;" + pdf
                markdown_text += "\n"
                law.append({"page_title": title,
                            "description": markdown_text,
                            "depth": 1})
        # 법령 정보 추출
        root_tag = xml_text.find('기본정보')
        book_info = {"book_title": root_tag.find('법령명_한글').text,
                     "enfc_dt": datetime.strptime(root_tag.find('시행일자').text, "%Y%m%d").date()}
        self.insert_db(law, book_info, username, target_sel)

    '''
    [ 행정규칙 마크다운 디자인 ]
     - 장 → H2 + 구분선
     - 절 → H2
     - 조문제목 → H3
     - 조문내용 → 디자인 없음, 이미지 처리
     - 별표제목 → 별표제목 + 파일링크
    '''
    def xml_to_markdown_admrul(self, xml_text, username, target_sel):
        admrul = []
        # 조문 컨버팅
        jo_root = xml_text.iter(tag='조문내용')
        for idx, jo in enumerate(jo_root):  # 조문 → H3
            jo = jo.text.lstrip().rstrip()
            if "(" in jo:
                title = jo.split("(", maxsplit=1)[0]
            else:
                title = jo.split(" ", maxsplit=1)[0]
            #전문(장)없이 조문(조)로만 구성된 경우, 행정규칙명으로 부모페이지 생성
            if idx == 0 and "장" not in title:
                book_title = xml_text.find('행정규칙기본정보').find('행정규칙명').text
                admrul.append({"page_title": book_title,
                               "description": "\n\n##" + book_title + "\n----------",
                               "depth": 0})
            # 장 → H2 + 구분선
            if "장" in title:
                admrul.append({"page_title": jo,
                               "description": "\n\n##" + jo + "\n----------",
                               "depth": 0})
            # 절 → H2
            elif "절" in title:
                admrul.append({"page_title": "null",
                               "description": "\n\n##" + jo + "\n",
                               "depth": 1})
            # 조 → H3, 조문내용 → 디자인 없음, 이미지 처리
            elif "조" in title:
                jo_context = jo.split(")", maxsplit=1)
                if len(jo_context) < 2:
                    description = "\n\n###" + jo_context[0] + "\n"
                else:
                    description = "\n\n###" + jo_context[0] + ")\n" + self.get_img_link(jo_context[1].replace("\n", "\n\n"))

                admrul.append({"page_title": jo_context[0].replace("(", " "),
                               "description": description,
                               "depth": 1})
        # 별표, 서식 컨버팅
        if len(xml_text.findall('별표')) > 0:
            # 별표/서식 목차 페이지 추가
            attachments_root = xml_text.iter(tag='별표단위')
            admrul.append({"page_title": "별표/서식",
                           "description": "\n\n##별표/서식 \n----------",
                           "depth": 0})
            for attachment in attachments_root:
                attachment_gb = attachment.find('별표구분').text
                order = "" if int(attachment.find('별표번호').text) == 0 else str(int(attachment.find('별표번호').text))
                order_branch = str(int(attachment.find('별표가지번호').text))
                if order_branch != "0":
                    order += "의" + order_branch
                if order == "":
                    order = attachment_gb + order
                else:
                    order = attachment_gb + " " + order
                title = "[" + order + "] " + attachment.find('별표제목').text.replace("&lt;", "<").replace("&gt;", ">")
                description = title
                if attachment.find("별표서식파일링크") is not None:
                    hwp = "[![](https://www.law.go.kr/LSW/images/button/btn_han.gif)](http://www.law.go.kr" \
                          + attachment.find("별표서식파일링크").text + ")"
                    description += "&nbsp;&nbsp;&nbsp;&nbsp;" + hwp
                if attachment.find("별표서식PDF파일링크") is not None:
                    pdf = "[![](https://www.law.go.kr/LSW/images/button/btn_pdf.gif)](http://www.law.go.kr" \
                          + attachment.find("별표서식PDF파일링크").text + ")"
                    description += "&nbsp;&nbsp;" + pdf + "\n"
                admrul.append({"page_title": title,
                               "description": description,
                               "depth": 1})
        # 행정규칙 정보 추출
        root_tag = xml_text.find('행정규칙기본정보')
        book_info = {"book_title": root_tag.find('행정규칙명').text,
                     "enfc_dt": datetime.strptime(root_tag.find('시행일자').text, "%Y%m%d").date()}
        self.insert_db(admrul, book_info, username, target_sel)

    '''
    [ 자치법규 마크다운 디자인 ]
     - 장 → H2 + 구분선
     - 절 → H2
     - 조문제목 → H3
     - 조문내용 → 디자인 없음, 이미지 처리
     - 별표제목 → 별표제목 + 파일링크
    '''
    def xml_to_markdown_ordin(self, xml_text, username, target_sel):
        ordin = []
        # 조문 컨버팅
        jo_root = xml_text.iter(tag='조')
        for idx, jo in enumerate(jo_root):
            jo_gunun = jo.find('조문여부').text
            jo_context = jo.find('조내용').text
            # 장없이 조로만 구성된 경우, 자치법규명으로 부모페이지 생성
            if idx == 0 and jo_gunun == "Y":
                book_title = xml_text.find('자치법규기본정보').find('자치법규명').text
                ordin.append({"page_title": book_title,
                              "description": "\n\n##" + book_title + "\n----------",
                              "depth": 0})
            # 장,절 → H2
            if jo_gunun == "N":
                jang_gubun = jo_context.split(" ", maxsplit=1)[0]
                if "장" in jang_gubun:
                    ordin.append({"page_title": jo_context,
                                  "description": "\n\n##" + jo_context + "\n----------",
                                  "depth": 0})
                elif "절" in jang_gubun:
                    ordin.append({"page_title": "null",
                                  "description": "\n\n##" + jo_context + "\n",
                                  "depth": 1})
            # 조 → H3, 조문내용 → 디자인 없음, 이미지 처리
            elif jo_gunun == "Y":
                jo_arr = jo_context.split(")", maxsplit=1)
                if len(jo_arr) < 2:
                    description = "\n\n###" + jo_arr[0] + "\n"
                else:
                    description = "\n\n###" + jo_arr[0] + ")\n" + self.get_img_link(jo_arr[1].replace("\n", "\n\n"))

                ordin.append({"page_title": jo_arr[0].replace("(", " "),
                              "description": description,
                              "depth": 1})
        # 별표, 서식 컨버팅
        if len(xml_text.findall('별표')) > 0:
            # 별표/서식 목차 페이지 추가
            attachments_root = xml_text.iter(tag='별표단위')
            ordin.append({"page_title": "별표/서식",
                          "description": "\n\n##별표/서식 \n----------",
                          "depth": 0})
            for attachment in attachments_root:
                page_title = attachment.find('별표제목').text
                attachment_gubun = attachment.find('별표첨부파일구분').text
                if attachment_gubun == "hwp":
                    file = "[![](https://www.law.go.kr/LSW/images/button/btn_han.gif)](" +\
                           attachment.find('별표첨부파일명').text + ")"
                elif attachment_gubun == "pdf":
                    file = "[![](https://www.law.go.kr/LSW/images/button/btn_pdf.gif)](" +\
                           attachment.find("별표첨부파일명").text + ")"
                elif attachment_gubun == "jpg":
                    file = "[![](https://www.law.go.kr/LSW/images/bullet/ico_fun03.gif)](" +\
                           attachment.find("별표첨부파일명").text + ")"
                ordin.append({"page_title": page_title,
                              "description": page_title + "&nbsp;&nbsp;&nbsp;&nbsp;" + file,
                              "depth": 1})
        # 자치법규 정보 추출
        root_tag = xml_text.find('자치법규기본정보')
        book_info = {"book_title": root_tag.find('자치법규명').text,
                     "enfc_dt": datetime.strptime(root_tag.find('시행일자').text, "%Y%m%d").date()}
        self.insert_db(ordin, book_info, username, target_sel)

    '''
    법규 내 이미지 링크 처리 function
    '''
    def get_img_link(self, context):
        img_start_tag = '<img id="'
        img_end_tag = '</img>'
        if img_start_tag in context and img_end_tag in context:
            return str(context.replace(
                img_start_tag, "\n![](https://www.law.go.kr/LSW/flDownload.do?flSeq=").replace(
                img_end_tag, ")\n").replace('">', ""))
        else:
            return context

    '''
    법규정보 DB저장 function
    '''
    def insert_db(self, page_list, book_info, username, target_sel):
        # 법규정보 Books 테이블 등록
        book = Books(
            book_title=book_info['book_title'], code_gubun=target_sel,
            author_id=username, codes_yn="Y", rls_yn="Y",
            enfc_dt=book_info['enfc_dt']
        )
        book.save()
        book_id = Books.objects.last().book_id
        try:
            # 법규정보 Pages 테이블 등록
            for page in page_list:
                depth = page.get('depth')
                if depth == 0:
                    parent_id = depth
                else:
                    parent_id = Pages.objects.filter(book_id=book_id, depth=0).last().page_id
                page = Pages(
                    book_id=book_id, parent_id=parent_id, depth=depth,
                    page_title=page.get('page_title'), description=page.get('description')
                )
                page.save()
        except Exception as e:
            # 페이지 저장 오류시 book 삭제
            Books.objects.get(book_id=book_id).delete()
            raise Exception






# 법규관리 페이지를 렌더링하는 function
@staff_member_required
def manage_law(request):
    context = {"books": Books.objects.filter(codes_yn="Y").order_by('-wrt_dt')}
    return render(request, "common/law_admin.html", context)


# 법규 공개여부를 번경하는 function
@staff_member_required
def law_update(request, book_id):
    law = Books.objects.get(book_id=book_id)
    if law.rls_yn == "Y":
        law.rls_yn = "N"
        result = "private"
    else:
        law.rls_yn = "Y"
        result = "public"
    law.save()
    return JsonResponse({"result": result})

# 법규 삭제 function
@staff_member_required
def law_delete(request, book_id):
    try:
        # 연관 북마크 삭제
        Bookmark.objects.filter(book_id=book_id).delete()
        # 연관 댓글 삭제
        page_list = Pages.objects.filter(book_id=book_id)
        for page in page_list:
            Comments.objects.filter(page_id=page.page_id).delete()
        # 하위 페이지들 삭제
        page_list.delete()
        # 페이지 삭제
        Books.objects.get(book_id=book_id).delete()
        return JsonResponse({"result": "success"})
    except Exception as e:
        return JsonResponse({"result": "fail", "message": "법규를 삭제하는 중 오류가 발생했습니다."})


# 회원관리 페이지를 렌더링하는 function
@staff_member_required
def manage_user(request):
    context = {"users": get_user_model().objects.all()}
    return render(request, "common/user_admin.html", context)


# 회원 활성화여부, 관리자여부를 변경하는 function
@staff_member_required
def user_update(request, user_id):
    user = get_user_model().objects.get(id=user_id)
    flag = request.GET.get('flag')
    if flag == 'is_active':
        if user.is_active == 0:
            user.is_active = 1
            message = "활성화"
        else:
            user.is_active = 0
            message = "휴면회원"
    elif flag == "is_staff":
        if user.is_staff == 0:
            user.is_staff = 1
            message = "관리자로 변경"
        else:
            user.is_staff = 0
            message = "일반회원으로 변경"
    user.save()
    return JsonResponse({"message": message})
