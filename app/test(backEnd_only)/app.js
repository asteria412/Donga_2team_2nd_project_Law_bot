// ============================================
// 📜 app.js - 메인 (공유 변수, 탭 전환, 초기화)
// ============================================

// 공유 변수 (다른 JS 파일에서도 접근 가능)
const badgeMap = {
    "👥 인사팀": "badge-hr",
    "🏢 총무팀": "badge-ga",
    "💼 회계팀": "badge-finance",
    "기타/공통": "badge-date"
};

let currentLaws = [];

// 💡 탭 전환 로직
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
    document.getElementById(tabId).style.display = 'block';

    document.querySelectorAll('.menu-item').forEach(el => el.classList.remove('active'));
    const activeMenu = document.querySelector(`.menu-item[data-tab="${tabId}"]`);
    if (activeMenu) {
        activeMenu.classList.add('active');
        const titleEl = document.getElementById('main-greeting-title');
        const descEl = document.getElementById('main-greeting-desc');

        switch (tabId) {
            case 'tab-feed':
                titleEl.innerHTML = "좋은 하루되세요, 경영지원본부 임직원 여러분! ☀️";
                descEl.innerHTML = "핵심 법령의 최신 업데이트 현황을 확인하세요.";
                break;
            case 'tab-search':
                titleEl.innerHTML = "판례/법령 AI 딥서치 🔍";
                descEl.innerHTML = "궁금한 법적 키워드를 입력하고 AI와 함께 딥다이브 해보세요.";
                break;
        }
    }
}

// 🚀 페이지 로드 시 초기화
document.addEventListener("DOMContentLoaded", () => {
    fetchLaws();
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab(item.getAttribute('data-tab'));
        });
    });
    document.querySelectorAll('input[name="dept"]').forEach(r => r.addEventListener('change', fetchLaws));
    document.getElementById('sort-order').addEventListener('change', fetchLaws);
    document.getElementById('display-cnt').addEventListener('change', fetchLaws);
});
