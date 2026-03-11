""" style/base_style.py
[전체 UI 스타일 시트] 무한개발공사의 'raw_bot' 프로젝트 전반의 디자인 가이드를 정의하는 CSS 설정 파일입니다.
서비스의 얼굴인 '무한raw봇'의 브랜드 이미지에 맞춘 Noto Sans KR 폰트 적용, 사이드바 커스텀, 
실시간 법령 피드의 카드 레이아웃 및 배지 스타일 등 시각적인 완성도를 총괄합니다. """

BASE_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

    :root {
        --primary-color: #1a73e8;
        --secondary-color: #606468;
        --bg-color: #f0f2f5;
        --card-bg: rgba(255, 255, 255, 0.9);
        --glass-bg: rgba(255, 255, 255, 0.7);
        --border-color: rgba(0, 0, 0, 0.05);
        --text-main: #1c1e21;
        --text-muted: #65676b;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
        background-color: var(--bg-color);
        color: var(--text-main);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid var(--border-color);
        box-shadow: 2px 0 10px rgba(0,0,0,0.02);
    }

    .sidebar-logo-container {
        /* 32px는 아래 라디오 버튼 아이콘 위치와 맞춘 값입니다 */
        padding: 20px 20px 20px 32px !important; 
        text-align: left !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important; /* 왼쪽으로 모으기 */
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 20px;
    }

    .sidebar-logo-img {
        width: 180px !important;
        border-radius: 12px;
        margin-bottom: 10px;
        margin-left: -75px !important;
        transition: transform 0.3s ease;
    }
    .sidebar-logo-img:hover {
        transform: scale(1.05);
    }

    /* Card Styling with Glassmorphism */

    /* Card Styling with Glassmorphism */
    .law-card {
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 24px;
        border: 1px solid var(--border-color);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
        margin-bottom: 14px;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        
        /* [핵심 1] 높이 고정 및 내부 정렬 선언 */
        height: 340px;
        display: flex;
        flex-direction: column;
    }

    .law-card-content {
        /* [핵심 2] 분홍색 여백을 6px로 확 줄이고, 남는 공간을 다 채우도록 함 */
        padding: 6px 24px; 
        display: flex;
        flex-direction: column;
        flex-grow: 1; /* 이 줄이 있어야 버튼이 바닥에 딱 붙습니다! */
    }

    .law-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.1);
        border-color: rgba(26, 115, 232, 0.2);
    }

    .law-badge-area {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 18px;
    }

    .law-dept-badge {
        background: rgba(26, 115, 232, 0.1);
        color: var(--primary-color);
        padding: 6px 16px;
        border-radius: 50px;
        font-size: 13px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .law-new-badge {
        background: #e6fcf5;
        color: #0ca678;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
    }

    .law-title {
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 12px;
        color: #1c1e21;
        margin-bottom: 16px;
        line-height: 1.4;
        height: 2.8em; 
        letter-spacing: -0.5px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }

    .law-info {
        font-size: 14px;
        color: var(--text-muted);
        margin-bottom: 6px;
        display: flex;
        align-items: flex-start;
        gap: 8px;
        line-height: 1.5;
    }

    .law-info b {
        white-space: nowrap;
        color: #495057;
    }

    /* Summary Cards */
    .summary-card-container {
        display: flex;
        gap: 20px;
        margin-bottom: 32px;
    }

    .summary-card {
        flex: 1;
        background: white;
        padding: 24px;
        border-radius: 20px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .summary-icon {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }

    .sum-val {
        font-size: 24px;
        font-weight: 700;
        color: #1c1e21;
    }

    .sum-label {
        font-size: 13px;
        color: var(--text-muted);
        font-weight: 500;
        margin-bottom: 2px;
    }

    /* Chat Styling */
    .stChatMessage {
        border-radius: 20px !important;
        padding: 15px !important;
        margin-bottom: 15px !important;
    }
    
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: white !important;
        border: 1px solid var(--border-color) !important;
        line-height: 1.7;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    [data-testid="stLinkButton"] a {
        height: 46px !important;
        border-radius: 12px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
</style>
"""
