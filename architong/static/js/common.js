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
