/**
 * 메인 페이지 네비게이션 클릭 이벤트
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
 * 메인 페이지 네비게이션 클릭 이벤트
 * */
function onclickProfilePagination(page_number) {
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
};

/**
 * 문자열 개행 함수 (textarea to html)
 * */
function displayNewLine(str) {
    if(typeof str == "string") {
        return str.replace(/\n/g, '<br/>');
    }
};

/**
 * 문자열 개행 함수 (template linebreaks to textarea)
 * PARAM : linebreaks 처리 된 p태그 배열
 * */
function displayNewLineReverse(strArr) {
    let content = "";
    for (let i in strArr) {
        let txt = strArr[i].innerHTML
        if (txt != undefined && txt != "") {
            content += txt.replace(/<br>/g, '\n');
            content += '\n\n';
        }
    }
    return content.slice(0, content.length - 2);
};

/**
 * 문자열 최소 길이 검토 함수
 * PARAM : 대상 컴포넌트 ID, 최소 길이
 * */
function checkMinLength(id, len) {
    const strLen = $("#" + id).val().length;
    if (strLen < Number(len)) {
        alert(len + "글자 이상 입력해야 합니다.");
        return false;
    } else {
        return true;
    }
};

/**
 * 댓글 좋아요 토글 이벤트
 * */
function onclickLikeComment(comment_id) {
    $.ajax({
        type: "GET",
        url: "/comment/like/" + comment_id,
        dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
        success: function (response) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
            let like = $("#like-count-" + comment_id);
            if (response.result == "add") {
                const like_count = Number(like.text()) + 1;
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
 * 현재 페이지의 URL 파라미터를 추출하는 함수
 * Param : 값을 추출하려고 하는 파라미터명
 * Return : 대상 파라미터의 값
 * */
function getUrlParam(sname) {
    let sval = "";
    const params = location.search.substr(location.search.indexOf("?") + 1).split("&");
    for (let i = 0; i < params.length; i++) {
        let temp = params[i].split("=");
        if ([temp[0]] == sname) {
            sval = temp[1];
        }
    }
    return sval;
};

/**
 * 컴포넌트 위치로 scroll을 이동시키는 함수
 * Param : 컴포넌트 ID, behavior 옵션
 * */
function moveScroll(id, behavior) {
    const point = document.querySelector('#' + id).offsetTop;      // 해당 컴포넌트의 좌표
    window.scrollTo({top: point, behavior: behavior});               // 해당 좌표로 스크롤 이동
};

/**
 * 정렬 콤보박스 변경 이벤트
 * */
function onchangeSort(value) {
    location.href = window.location.pathname + "?sort=" + value;
};

/**
 * 법규관리 페이지 법규구분 변경 이벤트
 * */
function onchangeTarget(value) {
    if (value == "0") {
        $("#target_no_label").html('법령MST&nbsp;&nbsp;<span id="description">' +
            '<i class="icon_error-circle_alt"></i>&nbsp;제목 입력 불가, 법령MST를 숫자로 입력해주세요.</span>');
    } else if (value == "1"){
        $("#target_no_label").html('행정규칙LID&nbsp;&nbsp;<span id="description">' +
            '<i class="icon_error-circle_alt"></i>&nbsp;제목 입력 불가, 행정규칙LID를 숫자로 입력해주세요.</span>');
    } else if (value == "2"){
        $("#target_no_label").html('자치법규MST&nbsp;&nbsp;<span id="description">' +
            '<i class="icon_error-circle_alt"></i>&nbsp;제목 입력 불가, 자치법규MST를 숫자로 입력해주세요.</span>');
    }
};

/**
 * inputbox 엔터키 감지
 */
$(document).ready(function(){
    $("#target_no").keypress(function (e) {
        if (e.which == 13) {
            onclickInsertLaw();
        }
    });
});

/**
 * 법규관리 페이지 법규 등록 이벤트
 * */
function onclickInsertLaw() {
    $.ajax({
        type: "POST",
        url: "/law",
        dataType: "json",
        data: $("#law_form").serialize() + "&csrfmiddlewaretoken=" + $("input[name=csrfmiddlewaretoken]").val(),
        success: function (response) {
            alert(response.message);
            if (response.result == "fail"){
                // 해당 법규 법제처 페이지 open
                window.open(response.html_url);
            } else if(response.result == "success") {
                document.location.href = "/law";
            }
        },
        error: function (request, status, error) {
            console.log("code:" + request.status + "\n" + "message:" + request.responseText + "\n" + "error:" + error)
        },
    });
};

/**
 * 법규관리 페이지 공개여부 변경 이벤트
 * */
function onclickLawRlsYn(book_id, book_title) {
    if(confirm(book_title + "의 공개여부를 변경하시겠습니까?")) {
       $.ajax({
            type: "PUT",
            url: "/law/" + book_id,
            headers: {
                "X-CSRFToken" : $("input[name=csrfmiddlewaretoken]").val()
            },
            dataType: "json",
            success: function (response) {
                if(response.result == "private") {
                    alert("해당 법규가 비공개 처리 되었습니다.");
                    document.location.href = "/law/manage";
                } else if (response.result == "public"){
                    alert("해당 법규가 공개 처리 되었습니다.");
                    document.location.href = "/law/manage";
                }
            },
            error: function (request, status, error) {
                console.log("code:" + request.status + "\n" + "message:" + request.responseText + "\n" + "error:" + error)
            },
       });
    }
};

/**
 * 법규관리 페이지 마크다운 디자인 수정 이벤트
 * */
function onclickUpdateLaw(book_id) {
    const page_id = selectPageId(book_id, 1);
    document.location.href = "/law/edit/" + page_id;
};

/**
 * 법규 수정 페이지 수정 이벤트
 * */
function onclickEditLaw(page_id) {
    let data = $("#page_form").serialize() + "&csrfmiddlewaretoken=" + $("input[name=csrfmiddlewaretoken]").val();
    // MDE context 별도 삽입
    if (simplemde.value() != null && simplemde.value() != "") {
        data += "&description=" + simplemde.value();
    }
    $.ajax({
        type: "POST",
        url: "/law/" + page_id,
        dataType: "json",
        data: data,
        success: function (response) {
            alert(response.message);
        },
        error: function (request, status, error) {
            console.log("code:" + request.status + "\n" + "message:"
                + request.responseText + "\n" + "error:" + error)
        },
   });
};

/**
 * 법규관리 페이지 법규 삭제 이벤트
 * */
function onclickDeleteLaw(book_id) {
    if (confirm("법규를 삭제하시면 하위 페이지 및 연관된 북마크, 댓글이 모두 삭제됩니다.\n정말 삭제하시겠습니까?")) {
        $.ajax({
            type: "DELETE",
            url: "/law/" + book_id,
            headers: {
                "X-CSRFToken" : $("input[name=csrfmiddlewaretoken]").val()
            },
            dataType: "json",
            success: function (response) {
                if(response.result == "success") {
                    document.location.href = "/law/manage";
                } else if (response.result == "fail"){
                    alert(response.message);
                }
            },
            error: function (request, status, error) {
                console.log("code:" + request.status + "\n" + "message:"
                    + request.responseText + "\n" + "error:" + error)
            },
       });
    }
};

/**
 * 회원관리 페이지 활성화여부 변경 이벤트
 * */
function onclickUserIsActive(userid, username, flag){
    const message = flag == "is_active" ? "활성화 여부를" :  "회원구분을";
    if(confirm(username + "님의 " + message + " 변경하시겠습니까?")) {
       $.ajax({
            type: "GET",
            url: "/user/" + userid + "?flag=" + flag,
            dataType: "json",
            success: function (response) {
                alert(username + "님이 " + response.message + " 처리 되었습니다.");
                document.location.href = "/user";
            },
            error: function (request, status, error) {
                console.log("code:" + request.status + "\n" + "message:" + request.responseText + "\n" + "error:" + error)
            },
       });
    }
};