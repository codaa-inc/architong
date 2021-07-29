/**
 * 전역변수 영역
 * */
let preSelId, preBmId = "" // 목록 클릭시 이전 선택값을 저장

/**
 * 법규 목록 클릭 이벤트
 * */
function onclickChildList(id, behavior) {
    const selId = 'page-' + id.replace('child-list-', '');                    // 해당 조문 ID
    const bmId = selId.replace("page", "bookmark")     // 해당 조문 북마크 ID
    if (behavior == "") {
        behavior = 'smooth';    // 문서내 이동시 behavior default = 'smooth'
    }
    moveScroll(selId, behavior); // 해당 위치로 스크롤 이동

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
 * 북마크 클릭 이벤트
 */
function onclikckBookMark(pageId) {
    // 삭제인 경우 북마크 하위 메모 삭제 여부를 확인한다.
    if ($("#bookmark-" + pageId).prop("title") == "북마크 삭제") {
        let commentCnt = getCommentCount(pageId, "N");
        if (commentCnt > 0) {
          if(!confirm("북마크를 삭제하시면 나의 비공개 메모 " + commentCnt +"건도 함께 삭제됩니다.\n진행하시겠습니까?")) {
                return;
            }
        }
        addOrRemoveBookmark(pageId);
    } else {
        // 추가인 경우 모달 오픈
        $('#selectProjectModal').appendTo("body").modal('show');
        $("#selectProjectModal").css("z-index", "1600");
        // 모달 속성 초기화
        $("#project_add").css('display', 'none');
        $("#bookmarkNewLabel").css('display', '');
        $("#project_select").removeAttr('disabled');
        $("#bookmarkParam").val(pageId);
    }
}

/**
 * 북마크 등록버튼 클릭 이벤트
 * */
function addBookmark() {
    // modal close
    $('#selectProjectModal').modal('hide');
    // 북마크 등록 요청
    const pageId = $("#bookmarkParam").val();
    addOrRemoveBookmark(pageId);
};

/**
 * 북마크 등록상태변경 함수
 * : 북마크 O → 북마크 삭제
 * : 북마크 X → 북마크 등록
 * */
function addOrRemoveBookmark(pageId) {
    $.ajax({
        type: "POST",
        url: "/book/bookmark/" + pageId,
        data: $("#bookmarkForm").serialize() + "&csrfmiddlewaretoken=" + $("input[name=csrfmiddlewaretoken]").val(),
        dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
        success: function (response) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
            if (response.result == "insert" || response.result == "delete") {
                window.location.href = "/page/" + pageId;
            } else if(response.result == "false") {
                if (confirm(response.message)) {
                    // 인증된 사용자가 아닌 경우 로그인 페이지로 이동
                    document.location.href = "/accounts/google/login/?next=" + window.location.pathname;
                }
            }
        },
        error: function (request, status, error) { // 통신 실패시 - 로그인 페이지 리다이렉트
            window.location.replace("/accounts/google/login/")
        },
    });
};

/**
 * 북마크 관리페이지 - 북마크 토글
 * */
function toggleBookmark(book_id) {
    const bookmarks = $("div[id^=" + 'book-' + book_id  + "]")
    if(bookmarks.css('display') == 'none') {
        bookmarks.show(200);
        $("#icon-" + book_id).attr('class', 'arrow_carrot-down')
    } else {
        bookmarks.hide(200);
        $("#icon-" + book_id).attr('class', 'arrow_carrot-up')
    }
};

/**
 * 북마크 관리페이지 - 북마크 삭제
 * */
function removeBookmark(pageId) {
    // 삭제하려는 경우 북마크 하위 메모 삭제 여부를 확인한다.
    if ($("#bookmark-" + pageId).prop("title") == "북마크 삭제") {
        let commentCnt = getCommentCount(pageId, "N");
        if(commentCnt > 0) {
            if(!confirm("북마크를 삭제하시면 나의 비공개 메모 " + commentCnt +"건도 함께 삭제됩니다.\n진행하시겠습니까?")) {
                return;
            }
        }
    }
    $.ajax({
        type: "DELETE",
        url: pageId,
        dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
        success: function (response) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
            if (response.result == "success") {
                $("div").remove("#page-" + pageId);
                $("#commentbox-" + pageId).remove();
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
                '<div class="media-body"><div class="comment_info"><div class="comment_date">' +
                '<a href="/profile/' + comment.username + '"><strong>' + comment.username + '</strong></a>' +
                '&nbsp;&nbsp;' + displayRegDt(comment.reg_dt);
            // 수정됨 표시
            if (comment.status == "U") {
                comment_html += "&nbsp;&nbsp;수정됨";
            }

            // 좋아요 표시
            if(comment.like_user_count != undefined) {
               comment_html += '<a id=' + "like-count-" + comment.comment_id  + ' class="count" ' +
                            'onclick="onclickLikeComment(' + "'" + comment.comment_id + "'" + ')" ' +
                            'style="margin-right: 85px;">';
               if (comment.is_liked === "true") {
                    comment_html += '<ion-icon name="heart"></ion-icon>';
               } else {
                    comment_html += '<ion-icon name="heart-outline"></ion-icon>';
               }
               comment_html += '&nbsp;' + comment.like_user_count + '</a>';
            }
            comment_html += '</div></div><p';

            // 임시저장 메세지 스타일 적용
            if (comment.status == "TD") {
                comment_html += ' style="color: rgba(0, 0, 0, 0.4); font-style: italic;"';
            }
            comment_html += '>' + displayNewLine(comment.content) + '</p>';
            // 자신의 글에 수정, 삭제 태그 추가
            if (USERNAME == comment.username && comment.status != "TD") {
                comment_html += '<a onclick="deleteComment(' + "'parent-" + comment.comment_id + "'" + ')" ' +
                    'class="comment_tag delete">&nbsp;삭제&nbsp;</a>';
                comment_html += '<a onclick="viewUpdateComment(' + "'parent-" + comment.comment_id + "'" + ')" ' +
                    'class="comment_tag">&nbsp;수정&nbsp;</a>';
            }
            comment_html += '<a onclick="viewCommentBox(' + "'child-" + comment.comment_id + "'" + ')" ' +
                'class="comment_reply">Reply <i class="arrow_right"></i></a></div></div>';

        } else if (comment.depth == 1) {
            comment_html += '<ul id="child-' + comment.comment_id + '" class="list-unstyled reply_comment">' +
                            '<li><div class="media comment_author"><div class="media-body"><div class="comment_info">' +
                            '<div class="comment_date"><a href="/profile/' + comment.username +'"><strong>' +
                            comment.username + '</strong></a>&nbsp;&nbsp;' + displayRegDt(comment.reg_dt);
            // 수정됨 표시
            if (comment.status === "U") {
                comment_html += "&nbsp;&nbsp;수정됨";
            }

            // 좋아요 표시
            if (comment.like_user_count != undefined){
                 comment_html += '<a id=' + "like-count-" + comment.comment_id  + ' class="count" ' +
                            'onclick="onclickLikeComment(' + "'" + comment.comment_id + "'" + ')">';
                 if (comment.is_liked === "true") {
                    comment_html += '<ion-icon name="heart"></ion-icon>';
                 } else {
                    comment_html += '<ion-icon name="heart-outline"></ion-icon>';
                 }
                 comment_html += '&nbsp;' + comment.like_user_count + '</a>'
            }
            comment_html += '</div></div><p>' + displayNewLine(comment.content) + '</p>';

            // 자신의 글에 수정, 삭제 태그 추가
            if (USERNAME == comment.username && comment.status != "TD") {
                comment_html += '<a onclick="deleteComment(' + "'child-" + comment.comment_id + "'" + ')" ' +
                    'class="comment_tag delete">&nbsp;삭제&nbsp;</a>';
                comment_html += '<a onclick="viewUpdateComment(' + "'child-" + comment.comment_id + "'" + ')" ' +
                    'class="comment_tag">&nbsp;수정&nbsp;</a>';
            }
            comment_html += '</div></div></li></ul>';
        }
    }

    // select할 경우 댓글창 새로 생성
    if (status == "select") {
       comment_html += '</li></ul></div>';
       $("#page-" + page_id).after(comment_html);

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

    ////////////////////  Depth 2 ////////////////////
    if (id.indexOf("parent") == -1) {
        let commentbox_html =
            '<div id="commentbox-' + id + '" class="blog_comment_box topic_comment" style="padding-top: 0px;">' +
            '<form id="form-' + id + '"  class="get_quote_form row"><div class="col-md-12 form-group">' +
            '<textarea id="textarea-' + id + '" name="content" class="form-control message" required></textarea>' +
            '<label class="floating-label">Comment</label></div><div class="col-md-12 form-group" id="radio-group">' +
            '<button class="action_btn btn_small" type="button" ' +
            'onclick="addComment(' + "'" + id + "'" + ')" style="color: #fff;">저장</button></div></form></div>';
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
                $('#commentbox-' + page_id).show();                 // 댓글창 show
            } else {
                $('#commentbox-' + page_id).hide(200, 'swing');     // 댓글창 hide
            }
        }

    ////////////////////  Depth 1 ////////////////////
    } else {
        let commentbox_html =
            '<div id="commentbox-' + id + '" class="blog_comment_box topic_comment" style="padding-top: 0px;">' +
            '<form id="form-' + id + '"  class="get_quote_form row"><div class="col-md-12 form-group">' +
            '<textarea id="textarea-' + id + '" name="content" class="form-control message" required></textarea>' +
            '<label class="floating-label">Comment</label></div><div class="col-md-12 form-group" id="radio-group">' +
            '<input type="radio" class="rls_yn" name="rls_yn" value="Y" id="rls_y" ' +
            'onchange="onchangeRadio(' + "'" + "rls_y" + "'" + ')" checked><label>공개 댓글</label>' +
            '<input type="radio" class="rls_yn" name="rls_yn" value="N" id="rls_n" ' +
            'onchange="onchangeRadio(' + "'" + "rls_n" + "'" + ')" style="margin-left: 10px;"><label>북마크 메모</label>' +
            '<button class="action_btn btn_small" type="button" ' +
            'onclick="addComment(' + "'" + id + "'" + ')" style="color: #fff;">저장</button></div></form></div>';
        $("#page-" + page_id).after(commentbox_html);
    }

    // 생성한 textarea로 마우스 커서 이동
    $('#textarea-' + id).focus();
};

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
    // 댓글 등록 POST 요청
    if (checkMinLength("textarea-" + id, 5)) {
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
                    // 비공개 메모일 경우 북마크 등록 표시
                    if(data.rls_yn == "N") {
                        $("#bookmark-" + data.page_id).children().attr("class", "icon_ribbon");
                        $("#bookmark-" + data.page_id).prop("title", "북마크 삭제");
                    }
                    // 해당 page의 comment count 증감
                    const comment_count = Number($("#comment-" + data.page_id).text()) + 1;
                    const comment_icon = '<ion-icon style="font-size: large" name="chatbubbles-outline"></ion-icon>&nbsp;';
                    $("#comment-" + data.page_id).html(comment_icon + comment_count);
                    // 댓글창 추가
                    viewCommentList(response, id, "insert");
                }
            },
            error: function (request, status, error) { // 통신 실패시 - 로그인 페이지 리다이렉트
                console.log("code:" + request.status + "\n" + "message:" + request.responseText + "\n" + "error:" + error)
                
            },
        });
    }
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
            '<textarea id="textarea-' + id + '" name="content" class="form-control message" required>'
            + edit_comment.text() + '</textarea>' +
            '<label class="floating-label">Comment</label></div><div class="col-md-12 form-group" id="radio-group">' +
            '<a class="doc_border_btn btn_small" type="button" onclick="viewUpdateComment(' + "'" + id + "'" + ')" ' +
            'style="margin-right: 10px; font-size: 16px;">취소</a>' +
            '<a class="action_btn btn_small" type="button" onclick="updateComment(' + "'" + id + "'" + ')" ' +
            'style="color: #fff;">저장</a></div></form></div>';
        // 댓글창 숨김, textarea 삽입
        edit_comment.hide();
        edit_comment.next().hide();
        edit_comment.next().next().hide();
        edit_comment.after(commentbox_html);
    }
};


/**
 * 댓글수정 요청함수
 * */
function updateComment(id) {
    // 댓글 수정 POST 요청
    if (checkMinLength("textarea-" + id, 5)) {
        $.ajax({
            type: "POST",
            url: "/comment/update/" + id,
            dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
            data: $("#form-" + id).serialize() + "&csrfmiddlewaretoken=" + $("input[name=csrfmiddlewaretoken]").val(),
            success: function (comment) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
                let comment_html = "";
                if (comment.depth == 0) {
                    comment_html += '<div id=' + "parent-" + comment.comment_id + ' class="media comment_author">' +
                         '<div class="media-body"><div class="comment_info"><div class="comment_date">' +
                        '<a href="/profile/' + comment.username +'"><strong>' + comment.username + '</strong></a>' +
                         '&nbsp;&nbsp;' + displayRegDt(comment.reg_dt) + '&nbsp;&nbsp;수정됨';

                    // 좋아요 표시
                    if(comment.like_user_count != undefined) {
                        comment_html += '<a id=' + "like-count-" + comment.comment_id  + ' class="count" ' +
                         'onclick="onclickLikeComment(' + "'" + comment.comment_id + "'" + ')" style="margin-right: 85px;">';
                        if (comment.is_liked === "true") {
                            comment_html += '<ion-icon name="heart"></ion-icon>';
                        } else {
                            comment_html += '<ion-icon name="heart-outline"></ion-icon>';
                        }
                        comment_html += '&nbsp;' + comment.like_user_count + '</a>';
                    }

                    comment_html += '</div></div><p>' + displayNewLine(comment.content) + '</p>' +
                         '<a onclick="deleteComment(' + "'parent-" + comment.comment_id + "'" + ')" class="comment_tag">&nbsp;삭제&nbsp;</a>' +
                         '<a onclick="viewUpdateComment(' + "'parent-" + comment.comment_id + "'" + ')" class="comment_tag">&nbsp;수정&nbsp;</a>' +
                         '<a onclick="viewCommentBox(' + "'child-" + comment.comment_id + "'" + ')" class="comment_reply">Reply ' +
                         '<i class="arrow_right"></i></a></div></div>';

                } else if (comment.depth == 1) {
                    comment_html += '<ul id="child-' + comment.comment_id + '" class="list-unstyled reply_comment">' +
                        '<li><div class="media comment_author"><div class="media-body"><div class="comment_info"><div class="comment_date">' +
                        '<a href="/profile/' + comment.username + '"><strong>' + comment.username + '</strong></a>&nbsp;&nbsp;' +
                        displayRegDt(comment.reg_dt) + '&nbsp;&nbsp;수정됨';

                        // 좋아요 표시
                        if (comment.like_user_count != undefined) {
                            comment_html += '<a id=' + "like-count-" + comment.comment_id  + ' class="count"' +
                                'onclick="onclickLikeComment(' + "'" + comment.comment_id + "'" + ')">';
                            if (comment.is_liked === "true") {
                                comment_html += '<ion-icon name="heart"></ion-icon>';
                            } else {
                                comment_html += '<ion-icon name="heart-outline"></ion-icon>';
                            }
                            comment_html += '&nbsp;' + comment.like_user_count + '</a>';
                        }

                    comment_html += '</div></div><p>' + displayNewLine(comment.content) + '</p>' +
                        '<a onclick="deleteComment(' + "'child-" + comment.comment_id + "'" + ')" class="comment_tag">&nbsp;삭제&nbsp;</a>' +
                        '<a onclick="viewUpdateComment(' + "'child-" + comment.comment_id + "'" + ')" class="comment_tag">&nbsp;수정&nbsp;</a>' +
                        '</div></div></li></ul>';
                }
                $("#" + id).replaceWith(comment_html);
            },
            error: function (request, status, error) { // 통신 실패시 - 로그인 페이지 리다이렉트
                console.log("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error)
                
            },
        });
    }
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
            
        },
    });
};

/**
 * 댓글 갯수 리턴하는 함수
 * PARAM : page_id, rls_yn
 * RETURN : comment count
 * */
function getCommentCount(page_id, rls_yn) {
    let commentCount = "";
    $.ajax({
        type: "GET",
        url: "/comment/count/?page_id=" + page_id + "&rls_yn=" + rls_yn,
        async : false,
        dataType: "json",
        success: function (response) {
            commentCount = Number(response.comment_count);
        },
        error: function (request, status, error) {

        },
    });
    return commentCount;
};

/**
 * 신규 책 등록 이벤트
 * */
function onclickSaveBook() {
    $.ajax({
        type: "POST",
        url: "/wiki/page",
        data: $("#wiki_register").serialize() + "&csrfmiddlewaretoken=" + $("input[name=csrfmiddlewaretoken]").val(),
        dataType: "json",
        success: function (response) {
            if (response.book_id != undefined) {
                document.location.href = "/wiki-editor/" + response.book_id;
            } else {
                alert(response.error_message);
            }
        },
        error: function (request, status, error) {
            console.log("code:" + request.status + "\n" + "message:" + request.responseText + "\n" + "error:" + error)
        },
    });
};

/**
 * 마크다운 에디터 페이지 수정 이벤트
 * */
function onclickSavePage(page_id) {
    let data = $("#page_form").serialize() + "&csrfmiddlewaretoken=" + $("input[name=csrfmiddlewaretoken]").val();
    // MDE context 별도 삽입
    if (simplemde.value() != null && simplemde.value() != "") {
        data += "&description=" + simplemde.value();
    }
    $.ajax({
        type: "POST",
        url: "/wiki-editor/page/" + page_id,
        data: data,
        dataType: "json",
        success: function (response) {
            if (response.page_id != undefined) {
                document.location.href = "/wiki/page/" + response.page_id;
            } else {
                alert(response.error_message);
            }
        },
        error: function (request, status, error) {
            console.log("code:" + request.status + "\n" + "message:" + request.responseText + "\n" + "error:" + error)
        },
    });
};

/**
 * 마크다운 에디터 페이지 추가 이벤트
 * */
function onclickAddPage(book_id, page_id) {
    if (page_id != "" && page_id != undefined) {
        // depth2에 추가
        document.location.href = "/wiki-editor/" + book_id + "?page=" + page_id;
    } else {
        // depth1에 추가
        document.location.href = "/wiki-editor/" + book_id;
    }
};

/**
 * 마크다운 에디터 페이지 삭제 이벤트
 * */
function onclickDeletePage(page_id) {
    if(confirm("페이지를 삭제하시면 하위 페이지 및 연관된 북마크, 댓글 모두 삭제됩니다.\n정말 삭제하시겠습니까?")) {
        $.ajax({
            type: "DELETE",
            url: "/wiki-editor/page/" + page_id,
            dataType: "json",
            headers: {
                "X-CSRFToken" : $("input[name=csrfmiddlewaretoken]").val()
            },
            success: function (response) {
                if (response.book_id != undefined) {
                    alert("삭제 되었습니다.");
                    document.location.href = "/wiki/" + response.book_id;
                } else {
                    alert("삭제 실패");
                }
            },
            error: function (request, status, error) {
                console.log("code:" + request.status + "\n" + "message:" + request.responseText + "\n" + "error:" + error)
            },
        });
    }
};

/**
 * 위키 수정 이벤트
 * */
function onclickUpdateWiki(book_id){
    $.ajax({
        type: "POST",
        url: "/wiki/" + book_id,
        data: $('#wiki').serialize() + "&csrfmiddlewaretoken=" + $("input[name=csrfmiddlewaretoken]").val(),
        dataType: "json",
        success: function (response) {
            alert(response.message);
            if (response.result == "success") {
                document.location.href = "/wiki/" + book_id;
            }
        },
        error: function (request, status, error) {
            console.log("code:" + request.status + "\n" + "message:" + request.responseText + "\n" + "error:" + error)
        },
    });
};

/**
 * 위키 삭제 이벤트
 * */
function onclickDeleteWiki(book_id){
    if(confirm("책을 삭제하시면 하위 페이지 및 연관된 북마크, 댓글 모두 삭제됩니다.\n정말 삭제하시겠습니까?")) {
        $.ajax({
            type: "DELETE",
            url: "/wiki/" + book_id,
            dataType: "json",
            headers: {
                "X-CSRFToken" : $("input[name=csrfmiddlewaretoken]").val()
            },
            success: function (response) {
                if (response.result == "success") {
                    alert("삭제 되었습니다.");
                    document.location.href = "/wiki";
                } else {
                    alert("삭제 실패");
                }
            },
            error: function (request, status, error) {
                console.log("code:" + request.status + "\n" + "message:" + request.responseText + "\n" + "error:" + error)
            },
        });
    }
};

/**
 * 뷰어 법규 및 위키 좋아요 클릭 이벤트
 * */
function onclickLikeBook(book_id) {
    $.ajax({
        type: "GET",
        url: "/book/like/" + book_id,
        dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
        success: function (response) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
            let like = $("#book-like-count");
            if (response.result == "add") {
                const like_count
                    = Number(like.text()) + 1;
                const like_icon = '<ion-icon name="heart" style="cursor: pointer;" title="좋아요 취소"></ion-icon>&nbsp;';
                like.html(like_icon + like_count);
            } else if(response.result == "remove") {
                const like_count = Number(like.text()) - 1;
                const like_icon = '<ion-icon name="heart-outline" style="cursor: pointer;" title="좋아요"></ion-icon>&nbsp;';
                like.html(like_icon + like_count);
            }
        },
        error: function (request, status, error) { // 통신 실패시 - 로그인 페이지 리다이렉트
            console.log("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error)
            
        },
    });
};


/**
 * 북마크 새폴더 추가 버튼 클릭 이벤트
 * */
function addNewProject() {
    $("#project_add").css('display', '');
    $("#bookmarkNewLabel").css('display', 'none');
    $("#project_select").val(0);
    $("#project_select").attr('disabled', 'disabled');
}

/**
 * 북마크 폴더관리 모달 오픈
 * */
function onclickFolderManage() {
    $('#selectProjectModal').appendTo("body").modal('show');
    $("#selectProjectModal").css("z-index", "1600");
};

/**
 *  북마크 폴더관리 모달 편집모드 클릭
 * */
function onclickEditMode(label_id) {
    // 모드 변환
    $("#label-" + label_id + "-view").css('display', 'none');
    $("#label-" + label_id + "-edit").css('display', '');
    // inputbox focus 설정
    const inputElem = $("#label-" + label_id + "-input");
    inputElem.focus();
    inputElem[0].setSelectionRange(inputElem.val().length, inputElem.val().length);
};

/**
 * 폴더관리 모달 리스트모드 클릭
 * */
function onclickViewMode(label_id) {
    setTimeout(function() {
        // 모드 변환
        $("#label-" + label_id + "-view").css('display', '');
        $("#label-" + label_id + "-edit").css('display', 'none');
    }, 300);
};

/**
 * 새폴더 추가 focusout 이벤트
 * */
function onclickNewLabelViewMode(){
    setTimeout(function() {
        $('#new_label').css('display', 'none');
    }, 300);
}

/**
 * 폴더관리 모달 새폴더 클릭
 * */
function onclickAddLabel() {
    if ($("#new_label").css('display') == 'none') {
        $("#new_label").css('display', '');
        $("#new_label_input").focus();
    }
};

/**
 * 북마크 폴더 추가
 * */
function addBookmarkLabel() {
    const newText = $("#new_label_input").val();
    $.ajax({
        type: "POST",
        url: "/bookmark/label/0",
        data: "label_name=" + newText + "&csrfmiddlewaretoken=" + $("input[name=csrfmiddlewaretoken]").val(),
        dataType: "json",
        success: function (response) {
            if (response.result == "success") {
                const newId = response.label_id;
                const newElem = '<li id="label-' + newId + '-view"><i class="icon_folder-alt"></i>&nbsp;' +
                    '<a id="label-' + newId + '" href="javascript:;" onclick="onclickEditMode(' + newId + ')">' +
                    newText + '</a></li><li id="label-' + newId + '-edit" style="display: none;">' +
                    '<i class="icon_folder-alt"></i>&nbsp;<input id="label-' + newId + '-input" name="label_name"' +
                    'value="' + newText + '" type="text" onfocusout="onclickViewMode(' + "'" + newId + "'" + ')">' +
                    '<a class="editMode" style="color: #0C0E72;" onclick="updateBookmarkLabel(' + newId + ')">수정</a>' +
                    '<a class="editMode" style="color: #C0392B;" ' +
                    'onclick="deleteBookmarkLabel(' + newId + ')">삭제</a></li>';
                // inputbox 초기화
                $("#new_label_input").val("");
                // 새폴더 추가
                $("#new_label").before(newElem);
            } else {
                alert("잘못된 접근입니다.");
            }
        },
        error: function (request, status, error) {
            console.log("code:" + request.status + "\n" + "message:" + request.responseText + "\n" + "error:" + error)
        },
    });
}

/**
 * 북마크 폴더 수정
 * */
function updateBookmarkLabel(label_id) {
    const newText = $("#label-" + label_id + "-input").val();
    $.ajax({
        type: "POST",
        url: "/bookmark/label/" + label_id,
        data: "label_name=" + newText + "&csrfmiddlewaretoken=" + $("input[name=csrfmiddlewaretoken]").val(),
        dataType: "json",
        success: function (response) {
            if (response.result == "success") {
                $("#label-" + label_id).text(newText);
            } else {
                alert("잘못된 접근입니다.");
            }
        },
        error: function (request, status, error) {
            console.log("code:" + request.status + "\n" + "message:" + request.responseText + "\n" + "error:" + error)
        },
    });
};

/**
 * 북마크 폴더 삭제
 * */
function deleteBookmarkLabel(label_id) {
    if (confirm("북마크 폴더를 삭제하시면 하위 북마크와 메모가 모두 삭제됩니다.\n삭제하시겠습니까?")) {
        $.ajax({
            type: "DELETE",
            url: "/bookmark/label/" + label_id,
            headers: { "X-CSRFToken" : $("input[name=csrfmiddlewaretoken]").val()},
            dataType: "json",
            success: function (response) {
                if (response.result == "success") {
                    $("#label-" + label_id + "-view").remove();
                    $("#label-" + label_id + "-edit").remove();
                } else {
                    alert("잘못된 접근입니다.");
                }
            },
            error: function (request, status, error) {
                console.log("code:" + request.status + "\n" + "message:" + request.responseText + "\n" + "error:" + error)
            },
        });
    }
};