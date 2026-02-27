// ============================================
// 🤖 quiz.js - AI 퀴즈 모달 팝업 로직
// ============================================

function openQuizModal() { document.getElementById('quiz-modal').style.display = 'flex'; }
function closeQuizModal() { document.getElementById('quiz-modal').style.display = 'none'; }

async function generateQuiz(index) {
    if (currentLaws.length === 0) { alert("퀴즈 데이터가 없습니다."); return; }
    const law = currentLaws[index];
    const quizContent = document.getElementById('quiz-modal-content');
    // 모달을 먼저 열고 로딩 표시
    quizContent.innerHTML = `<p style="text-align:center; padding:40px; font-size:15px; color:#2b6cee;">🤖 AI가 '${law.title}' 퀴즈를 출제 중... 🐟</p>`;
    openQuizModal();
    try {
        const response = await fetch('/api/quiz', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ law_name: law.title, enf_dt: law.enfDt, mst_id: law.mst_id }) });
        const quiz = await response.json();
        let optionsHTML = quiz.options.map(opt => `<button class="quiz-option" onclick="selectOption(this)" style="padding:14px 16px; font-size:14px; text-align:left; width:100%; background:white; border:1.5px solid #E5E7EB; border-radius:8px; cursor:pointer;">${opt}</button>`).join("");
        quizContent.innerHTML = `
            <div style="background-color:#EFF6FF; padding:18px; border-radius:10px; margin-bottom:20px; border-left:4px solid #2b6cee;">
                <p style="color:#0369a1; font-weight:700; font-size:15px; margin:0; line-height:1.6;">Q. ${quiz.question}</p>
            </div>
            <div style="display:flex; flex-direction:column; gap:10px; margin-bottom:20px;">${optionsHTML}</div>
            <button class="btn-primary" style="width:100%; padding:14px; font-size:15px;" onclick="submitQuiz('${quiz.answer.replace(/'/g, "\\'")}', '${quiz.explanation.replace(/'/g, "\\'")}')">${"정답 제출하기"}</button>
            <div id="quiz-result"></div>`;
    } catch (error) { quizContent.innerHTML = `<p style="color:red; text-align:center; padding:20px;">❌ 퀴즈 생성 실패.</p>`; }
}

function selectOption(element) {
    document.querySelectorAll('.quiz-option').forEach(o => { o.style.borderColor = "#E5E7EB"; o.style.backgroundColor = "white"; o.classList.remove('selected'); });
    element.style.borderColor = "#2b6cee"; element.style.backgroundColor = "#EFF6FF"; element.classList.add('selected');
}

function submitQuiz(correctAnswer, explanation) {
    const selected = document.querySelector('.quiz-option.selected');
    if (!selected) { alert("👉 보기를 먼저 선택하세요!"); return; }
    const resultDiv = document.getElementById('quiz-result');
    if (selected.innerText.trim().includes(correctAnswer)) {
        resultDiv.innerHTML = `<div style="margin-top:16px; padding:16px; background:#ECFDF5; border-radius:10px; border-left:4px solid #10B981;"><p style="font-weight:700; color:#065F46; font-size:15px; margin-bottom:8px;">🎉 정답입니다!</p><p style="color:#047857; font-size:13px; line-height:1.6;">${explanation}</p></div>`;
    } else {
        resultDiv.innerHTML = `<div style="margin-top:16px; padding:16px; background:#FEF2F2; border-radius:10px; border-left:4px solid #EF4444;"><p style="font-weight:700; color:#991B1B; font-size:15px; margin-bottom:8px;">앗, 오답입니다! 😭</p><p style="color:#B91C1C; font-size:13px; margin-bottom:8px;"><strong>[정답]</strong> ${correctAnswer}</p><p style="color:#7F1D1D; font-size:13px; line-height:1.6;">${explanation}</p></div>`;
    }
}
