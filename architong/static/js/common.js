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
 * 좋아요 토글 이벤트
 * */
function onclickLikeComment(commend_id) {
    $.ajax({
        type: "GET",
        url: "/comment/like/" + commend_id,
        dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
        success: function (response) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
            let like = $("#like-count-" + commend_id);
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
            //window.location.replace("/accounts/google/login/")
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
