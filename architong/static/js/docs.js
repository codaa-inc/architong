let preSelId, preBmId = "" // 목록 클릭시 이전 선택값을 저장하는 전역변수

/**
 * 페이지 네비게이션 클릭 이벤트
 * */
function onclickPagination(page_number) {
    const searchbox = $("#searchbox").val()
    // 검색어가 없으면 GET 요청, 검색어가 있으면 POST 요청(Form Submit)
    if (searchbox == "" || searchbox == null) {
        location.href ='?page=' + page_number;
    } else {
        $("#page").val(page_number);
        document.searchForm.submit();
    }
};

/**
 * 법규 목록 클릭시 스크롤을 이동시키는 함수
 * */
function onclickChildList(id) {
    const selId = 'page-' + id.replace('child-list-', '');                 // 해당 조문 ID
    const bmId = selId.replace("page", "bookmark")  // 해당 조문 북마크 ID
    const point = document.querySelector('#' + selId).offsetTop;  // 해당 조문의 좌표
    window.scrollTo({top: point, behavior: 'smooth'});             // 해당 좌표로 스크롤 이동

    // css toggle
    if (preSelId != "" && preBmId != "") {
        $('#' + preSelId).css('background-color', '');
        $('#' + preBmId).css('visibility', '');
    }
    $('#' + selId).css('background-color', '#F9F9F9');
    $('#' + bmId).css('visibility', 'visible');

    // 선택한 컴포넌트 ID 저장
    preSelId = selId;
    preBmId = bmId;
};

/**
 * 북마크 등록상태변경 함수
 * : 북마크 O → 북마크 삭제
 * : 북마크 X → 북마크 등록
 * */
function addOrRemoveBookmark(pageId) {
    $.ajax({
        type: "PUT",
        url: "bookmark/" + pageId,
        dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
        success: function (response) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
            if (response.result == "insert") {
                $("#bookmark-" + pageId).children().attr("class", "icon_ribbon");
                $("#bookmark-" + pageId).prop("title", "북마크 삭제");
            } else if (response.result == "delete"){
                // 북마크 삭제
                $("#bookmark-" + pageId).children().attr("class", "icon_ribbon_alt");
                $("#bookmark-" + pageId).prop("title", "북마크 등록");
            }
        },
        error: function (request, status, error) { // 통신 실패시 - 로그인 페이지 리다이렉트
            window.location.replace("/accounts/google/login/")
        },
    });
};

/**
 * 북마크 관리페이지 - 북마크 삭제
 * */
function removeBookmark(pageId) {
    $.ajax({
        type: "DELETE",
        url: pageId,
        dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
        success: function (response) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
            if (response.result == "success") {
                $("div").remove("#page-" + pageId);
            }
        },
        error: function (request, status, error) { // 통신 실패시 - 로그인 페이지 리다이렉트
            window.location.replace("/accounts/google/login/")
        },
    });
};

/**
 * 댓글 조회, 댓글창 생성
 * */
function viewComment(comment_count, page_id) {
    const status = $('#commentbox-' + page_id).css('display');
    if (status === 'none' ) {
        if(comment_count > 0) {     // 해당 게시물의 댓글이 존재하면 불러온다.
            $.ajax({
                type: "GET",
                url: "/comment/" + page_id,
                dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
                success: function (data) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
                    if (data.length > 0) {
                        let comment_html = '<div class="comment_inner"><ul class="comment_box list-unstyled"><li class="post_comment">';
                        for (let i in data) {
                            let comment = data[i].fields;
                            if (comment.depth == 0) {
                               comment_html += '<div class="media comment_author"><div class="media-body"><div class="comment_info">' +
                                            '<div class="comment_date"><strong>' + comment.username + '</strong>&nbsp;&nbsp;' +
                                            moment(comment.reg_dt).format('YYYY.MM.DD HH:mm') + '</div></div><p>' + comment.content + '</p>' +
                                            '<a href="#" class="comment_reply">Reply <i class="arrow_right"></i></a></div></div>';
                            } else if (comment.depth == 1) {
                                comment_html += '<ul class="list-unstyled reply_comment"><li><div class="media comment_author"><div class="media-body">' +
                                            '<div class="comment_info"><div class="comment_date"><strong>' + comment.username + '</strong>&nbsp;&nbsp;' +
                                            moment(comment.reg_dt).format('YYYY.MM.DD HH:mm') + '</div></div><p>' + comment.content + '</p></div></div></li></ul>';
                            }
                        }
                        comment_html += '</li></ul></div>';
                        comment_html.replace("{{ page.page_id }}", page_id);
                        $("#description-" + page_id).append(comment_html);
                    }
                },
                error: function (request, status, error) { // 통신 실패시 - 로그인 페이지 리다이렉트
                    window.location.replace("/accounts/google/login/")
                },
            });
        }
        $('#commentbox-' + page_id).show();     // 댓글창 toggle
    } else {
        $('#commentlist-' + page_id).hide();    // 댓글리스트 toggle
        $('#commentbox-' + page_id).hide();     // 댓글창 toggle
    }
};

/**
 * 댓글 radio toggle
 * */
function checkOne(id) {
    if (id == "rls_y") {
        $("input:checkbox[id='rls_n']").prop("checked", "false");
    } else {
        $("input:checkbox[id='rls_y']").prop("checked", "false");
    }
};

/**
 * 댓글작성함수
 * */
function addComment(page_id) {
    $.ajax({
        type: "POST",
        url: "/comment/" + page_id,
        dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
        success: function (response) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
            if (response.result == "success") {

            }
        },
        error: function (request, status, error) { // 통신 실패시 - 로그인 페이지 리다이렉트
            window.location.replace("/accounts/google/login/")
        },
    });
}