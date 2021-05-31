/**
 * 전역변수 영역
 * */
let preSelId, preBmId = "" // 목록 클릭시 이전 선택값을 저장

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
function onclickChildList(id, behavior) {
    if (behavior == "") {
        // 문서내 이동시 behavior default = 'smooth'
        behavior = 'smooth';
    }
    const selId = 'page-' + id.replace('child-list-', '');                       // 해당 조문 ID
    const bmId = selId.replace("page", "bookmark")     // 해당 조문 북마크 ID
    const point = document.querySelector('#' + selId).offsetTop;      // 해당 조문의 좌표
    window.scrollTo({top: point, behavior: behavior});                  // 해당 좌표로 스크롤 이동

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
            selectCommentList(page_id);
        }
        if (!document.getElementById('commentbox-parent-' + page_id)) {
            viewCommentBox("parent-" + page_id);        // 댓글창 생성
        } else {
            $('#commentbox-parent-' + page_id).remove();     // 댓글창 remove
        }
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
function selectCommentList(page_id) {
    $.ajax({
        type: "GET",
        url: "/comment/" + page_id,
        dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
        success: function (data) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
            if (data.length > 0) {
                viewCommentList(data, page_id, "select");
            }
        },
        error: function (request, status, error) { // 통신 실패시 - 로그인 페이지 리다이렉트
            console.log("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error)
            //window.location.replace("/accounts/google/login/")
        },
    });
}

/**
 * 댓글 리스트 생성
 * Param : data, page_id, status[select/insert]
 * */
function viewCommentList(data, page_id, status) {
    let comment_html = "";
    // depth1인 댓글을 insert 할때는 select와 동일한 로직 적용
    if (status == "insert" && data[0].depth == 0) {
        page_id = page_id.split('-')[1];
        status = "select";
    }
    // Append HTML
    if (status == "select") {
        comment_html = '<div id="commentlist-' + page_id + '" class="comment_inner">' +
                        '<ul class="comment_box list-unstyled"><li class="post_comment">';
    }
    for (let i in data) {
        let comment = data[i];
        if (comment.depth == 0) {
            comment_html += '<div id=' + "parent-" + comment.comment_id + ' class="media comment_author">' +
                '<div class="media-body"><div class="comment_info"><div class="comment_date"><strong>' + comment.username + '</strong>' +
                '&nbsp;&nbsp;' + displayRegDt(comment.reg_dt);
            // 수정됨 표시
            if (comment.status == "U") {
                comment_html += "&nbsp;&nbsp;수정됨";
            }
            comment_html += '</div></div><p';
            // 임시저장 메세지 스타일 적용
            if (comment.status == "TD") {
                comment_html += ' style="color: rgba(0, 0, 0, 0.4); font-style: italic;"';
            }
            comment_html += '>' + displayNewLine(comment.content) + '</p>';
            // 자신의 글에 수정, 삭제 태그 추가
            if (USERNAME == comment.username && comment.status != "TD") {
                comment_html += '<a onclick="deleteComment(' + "'parent-" + comment.comment_id + "'" + ')" class="comment_tag">&nbsp;삭제&nbsp;</a>';
                comment_html += '<a onclick="viewUpdateComment(' + "'parent-" + comment.comment_id + "'" + ')" class="comment_tag">&nbsp;수정&nbsp;</a>';
            }
            comment_html += '<a onclick="viewCommentBox(' + "'child-" + comment.comment_id + "'" + ')" class="comment_reply">Reply ' +
                            '<i class="arrow_right"></i></a></div></div>';
        } else if (comment.depth == 1) {
            comment_html += '<ul id="child-' + comment.comment_id + '" class="list-unstyled reply_comment">' +
                            '<li><div class="media comment_author"><div class="media-body"><div class="comment_info">' +
                            '<div class="comment_date"><strong>' + comment.username + '</strong>&nbsp;&nbsp;' +
                            displayRegDt(comment.reg_dt);
            // 수정됨 표시
            if (comment.status == "U") {
                comment_html += "&nbsp;&nbsp;수정됨";
            }
            comment_html += '</div></div><p>' + displayNewLine(comment.content) + '</p>'
            // 자신의 글에 수정, 삭제 태그 추가
            if (USERNAME == comment.username && comment.status != "TD") {
                comment_html += '<a onclick="deleteComment(' + "'child-" + comment.comment_id + "'" + ')" class="comment_tag">&nbsp;삭제&nbsp;</a>';
                comment_html += '<a onclick="viewUpdateComment(' + "'child-" + comment.comment_id + "'" + ')" class="comment_tag">&nbsp;수정&nbsp;</a>';
            }
            comment_html += '</div></div></li></ul>';
        }
    }

    // select할 경우 댓글창 새로 생성
    if (status == "select") {
       comment_html += '</li></ul></div>';
       $("#description-" + page_id).append(comment_html);

    // insert할 경우 댓글을 삽입할 위치를 탐색
    } else if(status == "insert") {
        const comment = data[0];
        let target_id = "";
        let nodeArr = $("#parent-" + comment.parent_id).nextAll();
        if (nodeArr.length < 1 || nodeArr[0].localName == "div") {
            target_id = "parent-" + comment.parent_id;
        } else {
            for (let i in nodeArr) {
                if (nodeArr[i].localName == "div") {
                    target_id = nodeArr[i - 1].id;
                    break;
                }
                if (i == nodeArr.length - 1 && target_id == "") {
                    target_id = nodeArr[i].id;
                }
            }
        }
        $("#" + target_id).after(comment_html);
    }
};

/**
 * 댓글창 생성
 * */
function viewCommentBox(id) {
    const page_id = id.split("-")[1];
    let commentbox_html = '<div id="commentbox-' + id + '" class="blog_comment_box topic_comment" style="padding-top: 0px;">' +
                            '<form id="form-' + id + '"  class="get_quote_form row"><div class="col-md-12 form-group">' +
                            '<textarea id="textarea-' + id + '" name="content" class="form-control message" required></textarea>' +
                            '<label class="floating-label">Comment</label></div><div class="col-md-12 form-group" id="radio-group">' +
                            '<input type="radio" class="rls_yn" name="rls_yn" value="Y" id="rls_y" onchange="onchangeRadio(' + "'" + "rls_y" + "'" + ')" checked><label>공개 댓글</label>' +
                            '<input type="radio" class="rls_yn" name="rls_yn" value="N" id="rls_n" onchange="onchangeRadio(' + "'" + "rls_n" + "'" + ')" style="margin-left: 10px;"><label>비공개 메모</label>' +
                            '<button class="action_btn btn_small" type="button" onclick="addComment(' + "'" + id + "'" + ')" style="color: #fff;">저장</button></div></form></div>';

    ////////////////////  Depth 2 ////////////////////
    if (id.indexOf("parent") == -1) {
        // 대댓글 창이 존재하지 않는 경우 생성
        if(!document.getElementById("commentbox-" + id)) {
            let targetId = "";
            const nodeArr = $("#parent-" + page_id).nextAll();
             // 다음 부모댓글이 없거나, 자식댓글이 없는 경우 현재 ID를 targetId로 지정
            if (nodeArr.length < 1 || nodeArr[0].localName == "div") {
                targetId = "parent-" + page_id;
            } else {
                for(let i in nodeArr) {
                    // 해당 부모 댓글에 다른 하위 댓글이 존재하는 경우 마지막 자식댓글 ID를 targetId로 지정
                    if (nodeArr[i].localName == "div") {
                        targetId = nodeArr[i - 1].id;
                        break;
                    }
                    // 맨 마지막 순서의 경우 자신의 ID를 targetId로 지정
                    if(targetId == "" || i == nodeArr.length -1) {
                        targetId = nodeArr[i].id;
                    }
                }
            }
            commentbox_html = '<ul class="list-unstyled reply_comment">' + commentbox_html + '</ul>';
            $("#" + targetId).after(commentbox_html);

        // 대댓글 창이 이미 존재하는 경우 toggle
        } else {
            if($('#commentbox-' + page_id).css('display') == 'none'){
                $('#commentbox-' + page_id).show();     // 댓글창 show
            } else {
                $('#commentbox-' + page_id).hide(200, 'swing');     // 댓글창 hide
            }
        }

    ////////////////////  Depth 1 ////////////////////
    } else {
        $("#description-" + page_id).after(commentbox_html);
    }

    // 생성한 textarea로 마우스 커서 이동
    $('#textarea-' + id).focus();
};

/**
// textarea enter key 입력시 저장 버튼 클릭 이벤트 실행
$('textarea[name=content]').click(function(){
    const id = $(this).attr('id').replace("textarea-", "");
    addComment(id);
});*/

/**
 * 댓글 radio toggle
 * */
function onchangeRadio(id) {
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
    // 글자수 체크
    const textLength = $("#textarea-" + id).val().length;
    if (textLength < 5) {
        alert("댓글은 5글자 이상 입력해야 합니다.");
        return;
    }
    // 댓글 등록 POST 요청
    $.ajax({
        type: "POST",
        url: "/comment/" + id,
        dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
        data: $("#form-" + id).serialize() + "&csrfmiddlewaretoken=" + $("input[name=csrfmiddlewaretoken]").val(),
        success: function (response) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
            if (response.result == "fail") {
                if (confirm(response.message)) {
                    // 인증된 사용자가 아닌 경우 로그인 페이지로 이동
                    document.location.href = "/accounts/google/login/?next=" + window.location.pathname;
                }
            } else if (response.length > 0) {
                const data = response[0];
                // 부모댓글일 경우 comment box 내용을 삭제
                if (data.depth == 0 && document.getElementById("textarea-" + id)) {
                    $("#textarea-" + id).val('');
                }
                // 자식댓글일 경우 comment box 요소를 삭제
                else if (data.depth == 1) {
                    $("#commentbox-" + id).parent().remove();
                }
                // 해당 page의 comment count 증감
                const comment_count = Number($("#comment-" + data.page_id).text()) + 1;
                const comment_icon  = '<ion-icon style="font-size: large" name="chatbubbles-outline"></ion-icon>&nbsp;';
                $("#comment-" + data.page_id).html(comment_icon + comment_count);
                // 댓글창 추가
                viewCommentList(response, id, "insert");
            }
        },
        error: function (request, status, error) { // 통신 실패시 - 로그인 페이지 리다이렉트
            console.log("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error)
            //window.location.replace("/accounts/google/login/")
        },
    });
};

/**
 * 댓글수정함수
 * */
function viewUpdateComment(id) {
    const edit_comment = $('#' + id).find('p');
    // 수정일때
    if (edit_comment.css('display') == 'none') {
        // textarea 삭제, 댓글창 삽입
        $('#commentbox-' + id).remove();
        edit_comment.show();
        edit_comment.next().show();
        edit_comment.next().next().show();
    }
    // 수정취소일때
    else {
        let commentbox_html = '<div id="commentbox-' + id + '" class="blog_comment_box topic_comment" style="padding-top: 0px;">' +
                                '<form id="form-' + id + '"  class="get_quote_form row"><div class="col-md-12 form-group">' +
                                '<textarea id="textarea-' + id + '" name="content" class="form-control message" required>' + edit_comment.text() + '</textarea>' +
                                '<label class="floating-label">Comment</label></div><div class="col-md-12 form-group" id="radio-group">' +
                                '<a class="doc_border_btn btn_small" type="button" onclick="viewUpdateComment(' + "'" + id + "'" + ')" style="margin-right: 10px; font-size: 16px;">취소</a>' +
                                '<a class="action_btn btn_small" type="button" onclick="updateComment(' + "'" + id + "'" + ')" style="color: #fff;">저장</a></div></form></div>';
        // 댓글창 숨김, textarea 삽입
        edit_comment.hide();
        edit_comment.next().hide();
        edit_comment.next().next().hide();
        edit_comment.after(commentbox_html);
    }
};


/**
 * 댓글수정함수
 * */
function updateComment(id) {
    // 글자수 체크
    const textLength = $("#textarea-" + id).val().length;
    if (textLength < 5) {
        alert("댓글은 5글자 이상 입력해야 합니다.");
        return;
    }
    // 댓글 수정 POST 요청
    $.ajax({
    type: "POST",
    url: "/comment/update/" + id,
    dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
    data: $("#form-" + id).serialize() + "&csrfmiddlewaretoken=" + $("input[name=csrfmiddlewaretoken]").val(),
    success: function (response) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
        if (response.length > 0) {
            let comment = response[0];
            let comment_html = "";
            if (comment.depth == 0) {
                comment_html += '<div id=' + "parent-" + comment.comment_id + ' class="media comment_author">' +
                     '<div class="media-body"><div class="comment_info"><div class="comment_date"><strong>' + comment.username + '</strong>' +
                     '&nbsp;&nbsp;' + displayRegDt(comment.reg_dt) + '&nbsp;&nbsp;수정됨</div></div><p>' +
                    displayNewLine(comment.content) + '</p>' +
                     '<a onclick="deleteComment(' + "'parent-" + comment.comment_id + "'" + ')" class="comment_tag">&nbsp;삭제&nbsp;</a>' +
                     '<a onclick="viewUpdateComment(' + "'parent-" + comment.comment_id + "'" + ')" class="comment_tag">&nbsp;수정&nbsp;</a>' +
                     '<a onclick="viewCommentBox(' + "'child-" + comment.comment_id + "'" + ')" class="comment_reply">Reply ' +
                     '<i class="arrow_right"></i></a></div></div>';
            } else if (comment.depth == 1) {
                comment_html += '<ul id="child-' + comment.comment_id + '" class="list-unstyled reply_comment">' +
                    '<li><div class="media comment_author"><div class="media-body"><div class="comment_info">' +
                    '<div class="comment_date"><strong>' + comment.username + '</strong>&nbsp;&nbsp;' +
                    displayRegDt(comment.reg_dt) + '&nbsp;&nbsp;수정됨</div></div><p>' +
                    displayNewLine(comment.content) + '</p>' +
                    '<a onclick="deleteComment(' + "'child-" + comment.comment_id + "'" + ')" class="comment_tag">&nbsp;삭제&nbsp;</a>' +
                    '<a onclick="viewUpdateComment(' + "'child-" + comment.comment_id + "'" + ')" class="comment_tag">&nbsp;수정&nbsp;</a>' +
                    '</div></div></li></ul>';
            }
            $("#" + id).replaceWith(comment_html);
        }
    },
    error: function (request, status, error) { // 통신 실패시 - 로그인 페이지 리다이렉트
        console.log("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error)
        //window.location.replace("/accounts/google/login/")
    },
});
}

/**
 * 댓글삭제함수
 * */
function deleteComment(id) {
    $.ajax({
        type: "DELETE",
        url: "/comment/" + id,
        headers: {
            "X-CSRFToken" : $("input[name=csrfmiddlewaretoken]").val()
        },
        dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
        success: function (response) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
            if (response.result != "fail") {
                // 해당 page의 comment count 증감
                const comment_count = Number($("#comment-" + id).text()) - 1;
                const comment_icon  = '<ion-icon style="font-size: large" name="chatbubbles-outline"></ion-icon>&nbsp;';
                $("#comment-" + id).html(comment_icon + comment_count);
                // delete → 해당 댓글란 삭제
                if (response.result == "delete") {
                    $("#" + id).remove();
                }
                // parent delete → 해당 댓글란 + 부모 댓글란 삭제
                else if (response.result == "parent delete") {
                    const prev_node = $("#" + id).prev()
                    $("#" + id).remove();
                    prev_node.remove();
                }
                // temporary delete → 내용 갈아끼움 ("이 댓글은 삭제되었습니다.")
                else if (response.result == "temporary delete") {
                    const node_arr = $("#" + id).children().children()
                    for (let i in node_arr) {
                        if (i == 1) {
                            node_arr[i].innerText = "이 댓글은 삭제되었습니다.";
                            node_arr[i].style.color = "rgba(0, 0, 0, 0.4)";
                            node_arr[i].style.fontStyle = "italic";
                        } else if (i == 2 || i == 3) {
                            node_arr[i].remove();
                        }
                    }
                }
            }
        },
        error: function (request, status, error) { // 통신 실패시 - 로그인 페이지 리다이렉트
            console.log("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error)
            //window.location.replace("/accounts/google/login/")
        },
    });
};

/**
 * 작성일 표시형식 변경 함수
 * */
function displayRegDt(reg_dt) {
    const milliSeconds = new Date() - new Date(reg_dt);
    const seconds = milliSeconds / 1000;
    if (seconds < 60) {
        return `방금 전`;
    }
    const minutes = seconds / 60;
    if (minutes < 60) {
        return `${Math.floor(minutes)}분 전`;
    }
    const hours = minutes / 60;
    if (hours < 24) {
        return `${Math.floor(hours)}시간 전`;
    }
    const days = hours / 24;
    if (days < 7) {
        return `${Math.floor(days)}일 전`
    }
    return moment(reg_dt).format('YYYY.MM.DD');
}

/**
 * 문자열 개행 함수
 * */
function displayNewLine(str) {
    if(typeof str == "string") {
        return str.replace(/\n/g, '<br/>');
    }
}