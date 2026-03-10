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
        padding: 20px;
        text-align: center;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 20px;
    }

    .sidebar-logo-img {
        width: 120px;
        border-radius: 12px;
        margin-bottom: 10px;
        transition: transform 0.3s ease;
    }
    .sidebar-logo-img:hover {
        transform: scale(1.05);
    }

    /* Card Styling with Glassmorphism */
    .law-card {
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 24px;
        border: 1px solid var(--border-color);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
        margin-bottom: 24px;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
    }

    .law-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.1);
        border-color: rgba(26, 115, 232, 0.2);
    }

    .law-card-content {
        padding: 32px;
        display: flex;
        flex-direction: column;
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
        font-size: 22px;
        font-weight: 700;
        color: #1c1e21;
        margin-bottom: 16px;
        line-height: 1.4;
        letter-spacing: -0.5px;
    }

    .law-info {
        font-size: 14px;
        color: var(--text-muted);
        margin-bottom: 8px;
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
</style>
"""
