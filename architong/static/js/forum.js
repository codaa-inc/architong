/**
 * 댓글상세페이지 댓글창 토글 이벤트
 * */
function onclickReply(commentId) {
    if($('#commentbox-' + commentId).css('display') == 'none') {
        $("#commentbox-" + commentId).show();
    } else {
        $("#commentbox-" + commentId).hide();
    }
}

/**
 * 댓글상세페이지 댓글 작성 이벤트
 * */
function addComment(id) {
    // 댓글 등록 POST 요청
    if (checkMinLength("textarea-" + id, 5)) {
        const csrftoken = "&csrfmiddlewaretoken=" + $("input[name=csrfmiddlewaretoken]").val();
        $.ajax({
            type: "POST",
            url: "/comment/" + "child-" + id,
            dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
            data: $("#form-" + id).serialize() + '&rls_yn=Y' + csrftoken,
            success: function (response) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
                if (response.result == "fail") {
                    if (confirm(response.message)) {
                        // 인증된 사용자가 아닌 경우 로그인 페이지로 이동
                        document.location.href = "/accounts/google/login/?next=" + window.location.pathname;
                    }
                } else if (response.length > 0) {
                    // 해당 페이지 리로딩
                    location.reload();
                }
            },
            error: function (request, status, error) { // 통신 실패시 - 로그인 페이지 리다이렉트
                console.log("code:" + request.status + "\n" + "message:" + request.responseText + "\n" + "error:" + error)
                //window.location.replace("/accounts/google/login/")
            },
        });
    }
};

/**
 * 댓글상세페이지 수정 댓글창 토글 이벤트
 * */
function viewUpdateComment(commentId) {
    const edit_comment = $('#comment-content-' + commentId).find('p');
    // 수정취소일때
    if (edit_comment.css('display') == 'none') {
        // textarea 삭제, 댓글창 삽입
        $('#commentbox-' + commentId).remove();
        edit_comment.show();
        edit_comment.next().show();
    }
    // 수정일때
    else {
        let commentbox_html = '<div id="commentbox-' + commentId + '" ' +
            'class="blog_comment_box topic_comment" style="padding-top: 0px;">' +
            '<form id="form-' + commentId + '"  class="get_quote_form row"><div class="col-md-12 form-group">' +
            '<textarea id="textarea-' + commentId + '" name="content" class="form-control message" required>' +
            displayNewLineReverse(edit_comment) + '</textarea>' +
            '<label class="floating-label">Comment</label></div><div class="col-md-12 form-group" id="radio-group">' +
            '<a class="doc_border_btn btn_small" type="button" onclick="viewUpdateComment(' + "'" + commentId + "'" + ')" ' +
            'style="margin-right: 10px; font-size: 16px;">취소</a>' +
            '<a class="action_btn btn_small" type="button" onclick="updateComment(' + "'" + commentId + "'" + ')" ' +
            'style="color: #fff;">저장</a></div></form></div>';
        // 댓글창 숨김, textarea 삽입
        edit_comment.hide();
        edit_comment.next().hide();
        edit_comment.parent().append(commentbox_html);
    }
};

/**
 * 댓글상세페이지 댓글 수정 이벤트
 * */
function updateComment(commentId) {
    // 댓글 수정 POST 요청
    if (checkMinLength("textarea-" + commentId, 5)) {
        $.ajax({
            type: "POST",
            url: "/comment/update/child-" + commentId,
            dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
            data: $("#form-" + commentId).serialize() + "&csrfmiddlewaretoken=" + $("input[name=csrfmiddlewaretoken]").val(),
            success: function (response) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
                if (response.length > 0) {
                    location.reload();
                }
            },
            error: function (request, status, error) { // 통신 실패시 - 로그인 페이지 리다이렉트
                console.log("code:" + request.status + "\n" + "message:" + request.responseText + "\n" + "error:" + error)
                //window.location.replace("/accounts/google/login/")
            },
        });
    }
};

/**
 * 댓글상세페이지 댓글 삭제 이벤트
 * */
function deleteComment(commentId) {
    $.ajax({
        type: "DELETE",
        url: "/comment/child-" + commentId,
        headers: {
            "X-CSRFToken" : $("input[name=csrfmiddlewaretoken]").val()
        },
        dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
        success: function (response) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
            if (response.result != "fail") {
                // 해당 페이지 리로딩
                location.reload();
            }
        },
        error: function (request, status, error) { // 통신 실패시 - 로그인 페이지 리다이렉트
            console.log("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error)
            //window.location.replace("/accounts/google/login/")
        },
    });
};
