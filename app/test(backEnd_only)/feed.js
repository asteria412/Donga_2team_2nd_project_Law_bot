// ============================================
// 📜 feed.js - 실시간 법령 피드 로직
// ============================================

// 백엔드 API 호출하여 법령 데이터 가져오기
async function fetchLaws() {
    const container = document.getElementById("law-feed-container");
    container.innerHTML = "<p style='grid-column: 1 / -1; text-align: center; padding: 40px;'>국가법령정보센터에서 실시간 데이터를 가져오는 중입니다... 🐟</p>";

    const deptChecked = document.querySelector('input[name="dept"]:checked');
    const dept = deptChecked ? deptChecked.parentNode.innerText.trim() : "전체";
    const sort = document.getElementById('sort-order').value;
    const count = document.getElementById('display-cnt').value;

    try {
        const response = await fetch(`/api/laws?dept=${encodeURIComponent(dept)}&sort_option=${sort}&display_cnt=${count}`);
        const data = await response.json();
        currentLaws = data.laws || [];
        const totalCount = data.total_count || 0;
        updateSummaryCards(currentLaws, totalCount);
        renderFeed(currentLaws, totalCount);
    } catch (error) {
        console.error("Failed to fetch laws", error);
        container.innerHTML = "<p style='color: red; grid-column: 1 / -1; text-align: center; padding: 40px;'>데이터를 불러오는데 실패했습니다.</p>";
    }
}

// 상단 요약 카드 업데이트
function updateSummaryCards(laws, total) {
    document.getElementById('summary-count').innerHTML = `${laws.length}<span class="unit">건</span>`;
    document.getElementById('summary-review').innerHTML = `${Math.ceil(laws.length * 0.3)}<span class="unit">건</span>`;
    document.getElementById('summary-ai').innerHTML = `100<span class="unit">%</span>`;
}

// 법령 카드 목록 렌더링
function renderFeed(laws, totalCount = 0) {
    const container = document.getElementById("law-feed-container");
    container.innerHTML = "";
    if (laws.length === 0) {
        let msg = "해당 조건의 최근 업데이트된 법령이 없습니다.";
        if (totalCount > 0) {
            msg += `<br><span style="font-size:13px; color:#6B7280;">(전체 ${totalCount}건의 법령이 검색되었으나 기준에 해당하지 않습니다)</span>`;
        }
        container.innerHTML = `<p style='grid-column: 1 / -1; text-align: center; padding: 40px;'>${msg}</p>`;
        return;
    }
    laws.forEach((law, index) => {
        const aiBadge = law.is_ai ? "✨[AI자동분류]" : "📍";
        const badgeClass = badgeMap[law.dept] || "badge-date";
        const cardHTML = `
            <div class="card glass-panel law-card">
                <div class="law-header">
                    <span class="badge ${badgeClass}">${aiBadge} ${law.dept}</span>
                    <span class="badge badge-date">NEW</span>
                </div>
                <h3 class="law-title">${law.title}</h3>
                <div class="law-meta">
                    <p><strong>공포:</strong> ${law.promDt} | <strong>시행:</strong> ${law.enfDt}</p>
                    <p><strong>주관:</strong> ${law.agency}</p>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 15px; align-items: center;">
                    <a href="https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=${law.mst_id}" target="_blank" style="color: #1e40af; font-weight: 600; text-decoration: none; font-size: 13px; white-space: nowrap;">👉 상세 조회</a>
                    <button onclick="generateQuiz(${index})" style="font-size: 11px; padding: 4px 10px; border: 1.5px solid #2b6cee; background: transparent; color: #2b6cee; border-radius: 6px; cursor: pointer; white-space: nowrap; width: auto; flex: none;">🤖 AI 퀴즈</button>
                </div>
            </div>`;
        container.insertAdjacentHTML("beforeend", cardHTML);
    });
}
