BASE_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
        background-color: #f8f9fa;
    }

    [data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid #eee;
        padding-top: 20px;
    }

    .sidebar-logo {
        padding: 0 20px 20px 20px;
        margin-bottom: 20px;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 20px !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        font-size: 18px !important;
        font-weight: 500 !important;
        color: #495057 !important;
    }

    /* 요약 카드 스타일 */
    .summary-card-container {
        display: flex;
        gap: 24px;
        margin-bottom: 30px;
    }
    .summary-card {
        flex: 1;
        background: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        display: flex;
        align-items: center;
        gap: 20px;
        border: 1px solid #f1f3f5;
    }
    .summary-icon {
        width: 56px;
        height: 56px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
    }
    .sum-val {
        font-size: 28px;
        font-weight: 700;
        color: #212529;
    }
    .sum-label {
        font-size: 14px;
        color: #868e96;
        margin-bottom: 4px;
    }

    .law-card {
        background: white;
        border-radius: 20px;
        border: 1px solid #f1f3f5;
        box-shadow: 0 4px 20px rgba(0,0,0,0.02);
        margin-bottom: 20px;
        overflow: hidden;
    }
    .law-card-content {
        padding: 30px;
        height: 240px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    .law-badge-area {
        display: flex;
        justify-content: space-between;
        margin-bottom: 15px;
    }
    .law-dept-badge {
        background: #f1f3f5;
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 13px;
        color: #495057;
        font-weight: 500;
    }
    .law-new-badge {
        background: #ebfbee;
        color: #40c057;
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 700;
    }
    .law-title {
        font-size: 20px;
        font-weight: 700;
        color: #212529;
        margin-bottom: 15px;
        line-height: 1.4;
    }
    .law-info {
        font-size: 14px;
        color: #868e96;
        margin-bottom: 8px;
    }
    .law-actions {
        background: #fcfdfe;
        border-top: 1px solid #f1f3f5;
        padding: 20px 30px;
        display: flex;
        gap: 15px;
    }
    .btn-detail {
        color: #4c6ef5;
        font-weight: 600;
        font-size: 15px;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 5px;
    }
</style>
"""
