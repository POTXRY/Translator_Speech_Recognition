// 회원가입 함수
function signup() {
    const username = $('#signup-username').val();
    const email = $('#signup-email').val();
    const password = $('#signup-password').val();
    const confirmPassword = $('#signup-confirm-password').val();  // 비밀번호 확인 입력

    // 입력값이 모두 채워졌는지 확인
    if (!username || !email || !password || !confirmPassword) {
        alert("모든 필드를 채워주세요."); // 경고 메시지
        return; // 빈 값이 있으면 함수 종료
    }

    // 비밀번호와 비밀번호 확인이 일치하는지 확인
    if (password !== confirmPassword) {
        alert("비밀번호가 일치하지 않습니다."); // 비밀번호 불일치 경고
        return;
    }

    // 서버로 보낼 데이터 객체
    const data = { username, email, password };

    // jQuery AJAX 요청
    $.ajax({
        url: '/signup',  // Flask 서버에서 회원가입을 처리하는 엔드포인트
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response) {
            alert(response.message); // 성공 메시지 출력
            if (response.redirect_url) {
                window.location.href = response.redirect_url;
            } 
        },
        error: function(error) {
            alert("Error: " + error.responseJSON.message); // 오류 메시지 출력
        }
    });
}
// 로그인 함수
function login() {
    const username = $.trim($('#login-username').val());  // 공백 제거
    const password = $.trim($('#login-password').val());  // 공백 제거

    // 입력값 확인
    if (!username || !password) {
        alert("모든 필드를 채워주세요.");
        return;
    }

    // 서버로 보낼 데이터 객체
    const data = { username, password };

    $.ajax({
        url: '/login/login',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        xhrFields: {
            withCredentials: true  // 쿠키 전송을 허용
        },
        success: function(response) {
            console.log('Logged in successfully');
            
            // 대시보드 페이지로 이동
            if (response.redirect_url) {
                window.location.href = response.redirect_url;
            } else {
                console.error('Redirect URL not provided by the server.');
                alert('로그인에 성공했지만, 페이지를 찾을 수 없습니다.');
            }
        },
        error: function() {
            alert('로그인 실패: 올바른 정보를 입력하세요.');
        }
    });
}




function logout() {
    $.ajax({
        url: '/login/logout',  // 로그아웃 엔드포인트 URL
        type: 'POST',
        xhrFields: {
            withCredentials: true  // 쿠키 전송을 허용
        },
        success: function(response) {
            console.log('Logged out successfully');

            // 서버 응답에서 리다이렉트 URL로 이동
            if (response.redirect_url) {
                window.location.href = response.redirect_url;
            } else {
                console.error('Redirect URL not provided by the server.');
                alert('로그아웃에 성공했지만, 페이지를 찾을 수 없습니다.');
            }
        },
        error: function() {
            alert('로그아웃 실패: 다시 시도해주세요.');
        }
    });
}