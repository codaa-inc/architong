let preSelId, preBmId = "" // 이전에 선택한 컴포넌트를 기억하기 위한 전역변수

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
}