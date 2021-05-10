let preSelId, preBmId = "" // 이전에 선택한 목록을 기억하기 위한 전역변수

function onclickChildList(id) {
    const selId = 'page-' + id.replace('child-list-', '');                 // 해당 조문 ID
    const bmId = selId.replace("page", "bookmark")  // 해당 조문 북마크 ID
    const point = document.querySelector('#' + selId).offsetTop;  // 해당 조문의 좌표
    window.scrollTo({top: point, behavior: 'smooth'});             // 해당 좌표로 스크롤 이동
    // css toggle
    $('#' + selId).css('background-color', '#F9F9F9');
    $('#' + bmId).css('visibility', 'visible');
    if (preSelId != "" && preBmId != "") {
        $('#' + preSelId).css('background-color', '');
        $('#' + preBmId).css('visibility', '');
    }
    preSelId = selId;       // 선택한 ID 저장
    preBmId = bmId;         // 선택한 북마크 ID 저장
};

function addBookmark(pageId) {
    $.ajax({
        type: "GET",
        url: "bookmark/" + pageId,
        dataType: "json", // 서버측에서 전송한 Response 데이터 형식 (json)
        success: function (response) { // 통신 성공시 - 동적으로 북마크 아이콘 변경
            if (response.result == true) {
                console.log("ajax 성공");
            }
            /**
            $("#count-" + pk).html(response.like_count + "개");
            var users = $("#like-user-" + pk).text();
            if (users.indexOf(response.nickname) != -1) {
                $("#like-user-" + pk).text(users.replace(response.nickname, ""));
            } else {
                $("#like-user-" + pk).text(response.nickname + users);
            }
             */
        },
        error: function (request, status, error) { // 통신 실패시 - 로그인 페이지 리다이렉트
            window.location.replace("/accounts/google/login/")
        },
    });
}