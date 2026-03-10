# 📋 변수명 사전 (Variable Dictionary)

> 팀원 모두가 참고하는 변수명 통일 규칙입니다.
> 새 기능 추가 시 이 문서에 맞춰 네이밍하세요.

---

## 1. 네이밍 규칙 (Naming Convention)

| 대상 | 규칙 | 예시 |
|------|------|------|
| **HTML ID** | `kebab-case` (소문자 + 하이픈) | `law-feed-container` |
| **CSS 클래스** | `kebab-case` | `glass-panel`, `btn-primary` |
| **JS 함수** | `camelCase` (동사로 시작) | `fetchLaws()`, `renderFeed()` |
| **JS 변수** | `camelCase` | `currentLaws`, `badgeMap` |
| **JS 상수** | `UPPER_SNAKE_CASE` | (현재 사용 안 함) |
| **API 엔드포인트** | `/api/소문자` | `/api/laws`, `/api/chat` |

---

## 2. HTML ID 목록

### 🗂️ 공통/레이아웃
| ID | 위치 | 설명 |
|----|------|------|
| `main-greeting-title` | 상단 인사말 | 탭별 변경되는 제목 |
| `main-greeting-desc` | 상단 인사말 | 탭별 변경되는 설명 |

### 📜 탭 컨테이너
| ID | 탭 | 설명 |
|----|-----|------|
| `tab-feed` | 실시간 피드 | 법령 업데이트 피드 영역 |
| `tab-search` | AI 딥서치 | 법령/판례 검색 영역 |
| `tab-chatbot` | AI 챗봇 | RAG 챗봇 영역 |
| `tab-calendar` | 캘린더 | 시행 예정 일정 영역 |
| `tab-alerts` | 알림 설정 | 맞춤 알림 영역 |

### 📜 피드 탭 (feed.js)
| ID | 설명 |
|----|------|
| `law-feed-container` | 법령 카드 목록이 렌더링되는 컨테이너 |
| `summary-count` | 상단 요약 - 업데이트 건수 |
| `summary-review` | 상단 요약 - 검토 필요 건수 |
| `summary-ai` | 상단 요약 - AI 분석률 |
| `sort-order` | 정렬 셀렉트박스 |
| `display-cnt` | 표시 건수 셀렉트박스 |

### 🔍 딥서치 탭 (search.js)
| ID | 설명 |
|----|------|
| `ai-search-input` | 검색 키워드 입력창 |
| `ai-search-results` | 검색 결과가 렌더링되는 컨테이너 |

### 💬 챗봇 탭 (chatbot.js)
| ID | 설명 |
|----|------|
| `chat-input` | 채팅 메시지 입력창 |
| `chat-history` | 채팅 기록이 렌더링되는 컨테이너 |


### 🤖 퀴즈 모달 (quiz.js)
| ID | 설명 |
|----|------|
| `quiz-modal` | 퀴즈 모달 전체 오버레이 |
| `quiz-modal-content` | 퀴즈 문제가 렌더링되는 영역 |
| `quiz-result` | 정답/오답 결과 표시 영역 |

---

## 3. CSS 클래스 목록

### 레이아웃
| 클래스 | 설명 |
|--------|------|
| `app-container` | 전체 앱 래퍼 (사이드바 + 메인) |
| `sidebar` | 좌측 네비게이션 바 |
| `main-content` | 우측 메인 콘텐츠 영역 |
| `menu-item` | 사이드바 메뉴 항목 |
| `tab-content` | 탭별 콘텐츠 래퍼 |

### 카드/패널
| 클래스 | 설명 |
|--------|------|
| `card` | 기본 카드 스타일 |
| `glass-panel` | 반투명 유리 효과 카드 |
| `law-card` | 법령 카드 |
| `summary-card` | 상단 요약 카드 |

### 법령 카드 내부
| 클래스 | 설명 |
|--------|------|
| `law-header` | 법령 카드 상단 (배지 영역) |
| `law-title` | 법령 제목 |
| `law-meta` | 공포일/시행일/주관 메타 정보 |

### 배지
| 클래스 | 용도 | 색상 |
|--------|------|------|
| `badge` | 배지 기본 스타일 | - |
| `badge-hr` | 인사/HR팀 | 파란색 계열 |
| `badge-ga` | 총무팀 | 녹색 계열 |
| `badge-finance` | 재무/회계팀 | 보라색 계열 |
| `badge-date` | 날짜/기타 | 회색 계열 |

### 버튼
| 클래스 | 설명 |
|--------|------|
| `btn-primary` | 메인 액션 버튼 (파란 배경) |
| `btn-primary-outline` | 보조 버튼 (테두리만) |

### 퀴즈
| 클래스 | 설명 |
|--------|------|
| `quiz-option` | 퀴즈 보기 버튼 |
| `selected` | 선택된 보기 표시 |

---

## 4. JS 함수 목록

### 📜 app.js (메인)
| 함수명 | 설명 |
|--------|------|
| `switchTab(tabId)` | 탭 전환 + 인사말 변경 |

### 📜 feed.js (피드)
| 함수명 | 설명 |
|--------|------|
| `fetchLaws()` | 백엔드 API 호출하여 법령 데이터 가져오기 |
| `updateSummaryCards(laws, total)` | 상단 요약 카드 숫자 업데이트 |
| `renderFeed(laws, totalCount)` | 법령 카드 목록 HTML 생성 및 렌더링 |

### 🤖 quiz.js (퀴즈)
| 함수명 | 설명 |
|--------|------|
| `openQuizModal()` | 퀴즈 모달 열기 |
| `closeQuizModal()` | 퀴즈 모달 닫기 |
| `generateQuiz(index)` | 법령 인덱스로 AI 퀴즈 생성 요청 |
| `selectOption(element)` | 보기 선택 시 UI 하이라이트 |
| `submitQuiz(correctAnswer, explanation)` | 정답 확인 및 결과 표시 |

### 🔍 search.js (딥서치)
| 함수명 | 설명 |
|--------|------|
| `performDeepSearch()` | AI 딥서치 실행 |

### 💬 chatbot.js (챗봇)
| 함수명 | 설명 |
|--------|------|
| `sendChatMessage()` | 채팅 메시지 전송 (RAG: Tavily+법령API+GPT) |
| `appendChatMessage(role, text)` | 채팅 말풍선 UI 추가 |


---

## 5. JS 공유 변수 (app.js에서 선언)

| 변수명 | 타입 | 설명 |
|--------|------|------|
| `badgeMap` | `Object` | 부서명 → CSS 배지 클래스 매핑 |
| `currentLaws` | `Array` | 현재 피드에 표시된 법령 목록 (퀴즈에서 참조) |

---

## 6. API 엔드포인트

| 메서드 | 경로 | 설명 | 사용 파일 |
|--------|------|------|-----------|
| `GET` | `/api/laws` | 법령 목록 조회 | feed.js |
| `POST` | `/api/search` | AI 딥서치 | search.js |
| `POST` | `/api/chat` | AI 법무 챗봇 (RAG) | chatbot.js |

---

## 7. 신규 기능 추가 시 체크리스트

1. ✅ HTML ID는 `kebab-case`로 작성
2. ✅ JS 함수는 `camelCase` + 동사로 시작
3. ✅ 새 JS 파일은 `js/` 폴더에 생성
4. ✅ `index.html`에 `<script src="js/파일명.js?v=N">` 추가
5. ✅ 이 문서에 새 변수/함수/ID 추가
