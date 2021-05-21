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
    const selId = 'page-' + id.replace('child-list-', '');                       // 해당 조문 ID
    const bmId = selId.replace("page", "bookmark")     // 해당 조문 북마크 ID
    const point = document.querySelector('#' + selId).offsetTop;      // 해당 조문의 좌표
    window.scrollTo({top: point, behavior: 'smooth'});                  // 해당 좌표로 스크롤 이동

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
 * 댓글 조회, 댓글창 toggle
 * */
function onclickComment(comment_count, page_id) {
    // 댓글창이 존재하지 X  → 해당 페이지의 댓글을 조회하고 댓글창을 생성한다
    if (!document.getElementById('commentlist-' + page_id)) {
        if(comment_count > 0) {
            // 해당 게시물의 댓글이 존재하면 불러오고 댓글리스트를 생성한다.
            requestCommentList(page_id);
        }
        viewCommentBox("parent-" + page_id);   // 댓글창 생성
    // 댓글창이 이미 생성되어 있으면 → 댓글리스트와 댓글창을 토글한다
    } else {
        if($('#commentlist-' + page_id).css('display') == 'none' || $('#commentbox-' + page_id).css('display') == 'none'){
            $('#commentlist-' + page_id).show();            // 댓글리스트 show
            $('#commentbox-parent-' + page_id).show();      // 댓글창 show
        } else {
            $('#commentlist-' + page_id).hide(200, 'swing');            // 댓글리스트 hide
            $('#commentbox-parent-' + page_id).hide(200, 'swing');      // 댓글창 hide
        }
    }
};

/**
 * 댓글 목록 요청
 * */
function requestCommentList(page_id) {
    $.ajax({
        type: "GET",
        url: "/comment/" + page_id,
        dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
        success: function (data) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
            if (data.length > 0) {
                viewCommentList(data, page_id);
            }
        },
        error: function (request, status, error) { // 통신 실패시 - 로그인 페이지 리다이렉트
            window.location.replace("/accounts/google/login/")
        },
    });
}

/**
 * 댓글 리스트 생성
 * */
function viewCommentList(data, page_id) {
    let comment_html = '<div id="commentlist-' + page_id + '" class="comment_inner"><ul class="comment_box list-unstyled"><li class="post_comment">';
    for (let i in data) {
        let comment = data[i].fields;
        let comment_id = String(data[i].pk);
        if (comment.depth == 0) {
            comment_html += '<div id=' + "parent-" + comment_id + ' class="media comment_author"><div class="media-body"><div class="comment_info">' +
                        '<div class="comment_date"><strong>' + comment.username + '</strong>&nbsp;&nbsp;' +
                        moment(comment.reg_dt).format('YYYY.MM.DD HH:mm') + '</div></div><p>' + comment.content + '</p>' +
                        '<a onclick="viewCommentBox(' + "'child-" + comment_id + "'" + ')" class="comment_reply">Reply <i class="arrow_right"></i></a></div></div>';
        } else if (comment.depth == 1) {
            comment_html += '<ul id="child-' + comment_id + '" class="list-unstyled reply_comment"><li><div class="media comment_author"><div class="media-body">' +
                        '<div class="comment_info"><div class="comment_date"><strong>' + comment.username + '</strong>&nbsp;&nbsp;' +
                        moment(comment.reg_dt).format('YYYY.MM.DD HH:mm') + '</div></div><p>' + comment.content + '</p></div></div></li></ul>';
        }
    }
    comment_html += '</li></ul></div>';
    $("#description-" + page_id).append(comment_html);
};

/**
 * 댓글창 생성
 * */
function viewCommentBox(id) {
    const page_id = id.split("-")[1];
    let commentbox_html = '<div id="commentbox-' + id + '" class="blog_comment_box topic_comment" style="padding-top: 0px;">' +
                            '<form id="form-' + id + '"  class="get_quote_form row"><div class="col-md-12 form-group">' +
                            '<textarea name="content" class="form-control message" required></textarea>' +
                            '<label class="floating-label">Comment</label></div><div class="col-md-12 form-group" id="radio-group">' +
                            '<input type="radio" class="rls_yn" name="rls_yn" value="Y" id="rls_y" onchange="checkOne(' + "'" + "rls_y" + "'" + ')" checked><label>공개 댓글</label>' +
                            '<input type="radio" class="rls_yn" name="rls_yn" value="N" id="rls_n" onchange="checkOne(' + "'" + "rls_n" + "'" + ')" style="margin-left: 10px;"><label>비공개 메모</label>' +
                            '<button class="action_btn btn_small" type="button" onclick="addComment(' + "'" + id + "'" + ')" style="color: #fff;">저장</button></div></form></div>';

    if (id.indexOf("parent") == -1) {       // depth 2
        if(!document.getElementById("commentbox-" + id)) {  // 대댓글 창이 존재하지 않는 경우 생성
            let targetId = "";
            const nodeArr = $("#parent-" + page_id).nextAll();
            for(let i in nodeArr) {
                // 다음 부모댓글이 존재하는 경우 바로 위 ID를 targetId로 지정
                if (nodeArr[i].localName == "div") {
                    targetId = nodeArr[i - 1].id;
                    break;
                }
                // 다음 부모댓글이 없는 경우 마지막 ID를 targetId로 지정
                if (i == nodeArr.length - 1 && targetId == "") {
                    targetId = nodeArr[i].id;
                }
            }
            commentbox_html = '<ul class="list-unstyled reply_comment">' + commentbox_html + '</ul>';
            $("#" + targetId).after(commentbox_html);
        } else {    // 대댓글 창이 이미 존재하는 경우 toggle
            if($('#commentbox-' + page_id).css('display') == 'none'){
                $('#commentbox-' + page_id).show();     // 댓글창 show
            } else {
                $('#commentbox-' + page_id).hide(200, 'swing');     // 댓글창 hide
            }
        }
    } else {        // depth 1
        $("#description-" + page_id).after(commentbox_html);
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
function addComment(id) {
    let formData = $("#form-" + id).serialize();
    formData += "&csrfmiddlewaretoken=" + $("input[name=csrfmiddlewaretoken]").val();
    $.ajax({
        type: "POST",
        url: "/comment/" + id,
        dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
        data: formData,
        success: function (response) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
            if (response.result == "success") {


            }
        },
        error: function (request, status, error) { // 통신 실패시 - 로그인 페이지 리다이렉트
            //window.location.replace("/accounts/google/login/")
        },
    });
}