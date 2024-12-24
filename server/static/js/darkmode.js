function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const button = document.getElementById('mode-toggle-btn');

    // 다크 모드 상태에 따라 localStorage 및 버튼 스타일 설정
    if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('theme', 'dark');
        document.getElementById('dark-icon').hidden = false;
        document.getElementById('light-icon').hidden = true;

        // 다크 모드 버튼 스타일
        button.classList.add('btn-dark');
        button.classList.remove('btn-light');
    } else {
        localStorage.setItem('theme', 'light');
        document.getElementById('dark-icon').hidden = true;
        document.getElementById('light-icon').hidden = false;

        // 라이트 모드 버튼 스타일
        button.classList.add('btn-light');
        button.classList.remove('btn-dark');
    }
}

// 페이지 로드 시 이전 테마 상태 적용
window.onload = function() {
    const theme = localStorage.getItem('theme');
    const button = document.getElementById('mode-toggle-btn');
    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
        document.getElementById('dark-icon').hidden = false;
        document.getElementById('light-icon').hidden = true;
        button.classList.add('btn-dark');
    } else {
        document.getElementById('dark-icon').hidden = true;
        document.getElementById('light-icon').hidden = false;
        button.classList.add('btn-light');
    }
};