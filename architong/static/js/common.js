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
 * 문자열 개행 함수
 * */
function displayNewLine(str) {
    if(typeof str == "string") {
        return str.replace(/\n/g, '<br/>');
    }
};

/**
 * 문자열 개행 복구 함수
 * */
function displayNewLineReverse(str) {
    if(typeof str == "string") {
        return str.replace('<br/>', '\n');
    }
};