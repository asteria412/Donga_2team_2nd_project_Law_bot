## 📚 국가법령정보센터 오픈 API 가이드북

- 지정 사이트에서 오픈 법령정보/오픈 API를 활용하고자 한다면 개인정보를 정확하게 기입해 주시기 바랍니다.
- 사이트 등록 후 openAPI를 이용하실 경우, 기관코드(OC)는 로그인 하신 이메일의 ID값을 사용하시면 됩니다.

---
## OC 는 국가법령정보센터 로그인 아이디임(@email.com 앞의 것)
---

## 1. 신구법 목록 조회 가이드 (완료)
※ 체계도 등 부가서비스는 법령서비스 신청을 하면 추가신청 없이 이용가능합니다.
- 요청 URL : http://www.law.go.kr/DRF/lawSearch.do?target=oldAndNew
요청 변수 (request parameter)
요청변수	값	설명
OC	string(필수)	사용자 이메일의 ID(g4c@korea.kr일경우 OC값=g4c)
target	string : oldAndNew(필수)	서비스 대상
type	char(필수)	출력 형태 HTML/XML/JSON
query	string	법령명에서 검색을 원하는 질의
display	int	검색된 결과 개수 (default=20 max=100)
page	int	검색 결과 페이지 (default=1)
sort	string	정렬옵션(기본 : lasc 법령오름차순)
ldes : 법령내림차순
dasc : 공포일자 오름차순
ddes : 공포일자 내림차순
nasc : 공포번호 오름차순
ndes : 공포번호 내림차순
efasc : 시행일자 오름차순
efdes : 시행일자 내림차순
efYd	string	시행일자 범위 검색(20090101~20090130)
ancYd	string	공포일자 범위 검색(20090101~20090130)
date	int	공포일자 검색
nb	int	공포번호 검색
ancNo	string	공포번호 범위 검색 (10000~20000)
rrClsCd	string	법령 제개정 종류
(300201-제정 / 300202-일부개정 / 300203-전부개정
300204-폐지 / 300205-폐지제정 / 300206-일괄개정
300207-일괄폐지 / 300209-타법개정 / 300210-타법폐지
300208-기타)
org	string	소관부처별 검색(소관부처코드 제공)
knd	string	법령종류(코드제공)
gana	string	사전식 검색 (ga,na,da…,etc)
popYn	string	상세화면 팝업창 여부(팝업창으로 띄우고 싶을 때만 'popYn=Y')
샘플 URL
1. 자동차관리법 신구법 HTML 조회
http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=oldAndNew&type=HTML&query=자동차관리법
2. 시행일자 범위 신구법 HTML 조회
http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=oldAndNew&type=HTML&efYd=20150101~20150131
3. 신구법 XML 조회
http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=oldAndNew&type=XML
4. 신구법 JSON 조회
http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=oldAndNew&type=JSON
출력 결과 필드(response field)
필드	값	설명
target	string	검색서비스 대상
키워드	string	검색 단어
section	string	검색범위
totalCnt	int	검색 건수
page	int	현재 페이지번호
numOfRows	int	페이지 당 출력 결과 수
resultCode	int	조회 여부(성공 : 00 / 실패 : 01)
resultMsg	int	조회 여부(성공 : success / 실패 : fail)
oldAndNew id	int	검색 결과 순번
신구법
일련번호	int	신구법 일련번호
현행연혁구분	string	현행연혁코드
신구법명	string	신구법명
신구법ID	int	신구법ID
공포일자	int	공포일자
공포번호	int	공포번호
제개정구분명	string	제개정구분명
소관부처코드	int	소관부처코드
소관부처명	string	소관부처명
법령구분명	string	법령구분명
시행일자	int	시행일자
신구법
상세링크	string	신구법 상세링크

## 2. [신구법 본문 조회]
※ 체계도 등 부가서비스는 법령서비스 신청을 하면 추가신청 없이 이용가능합니다.
- 요청 URL : http://www.law.go.kr/DRF/lawService.do?target=oldAndNew
요청 변수 (request parameter)
요청변수	값	설명
OC	string(필수)	사용자 이메일의 ID(g4c@korea.kr일경우 OC값=g4c)
target	string : oldAndNew(필수)	서비스 대상
type	char(필수)	출력 형태 : HTML/XML/JSON
ID	char	법령 ID (ID 또는 MST 중 하나는 반드시 입력)
MST	char	법령 마스터 번호 - 법령테이블의 lsi_seq 값을 의미함
LM	string	법령의 법령명(법령명 입력시 해당 법령 링크)
LD	int	법령의 공포일자
LN	int	법령의 공포번호
샘플 URL
1. 신구법 HTML 상세조회
http://www.law.go.kr/DRF/lawService.do?OC=test&target=oldAndNew&ID=000170&MST=122682&type=HTML
http://www.law.go.kr/DRF/lawService.do?OC=test&target=oldAndNew&MST=136931&type=HTML
2. 신구법 XML 상세조회
http://www.law.go.kr/DRF/lawService.do?OC=test&target=oldAndNew&MST=122682&type=XML
3. 신구법 JSON 상세조회
http://www.law.go.kr/DRF/lawService.do?OC=test&target=oldAndNew&MST=122682&type=JSON
출력 결과 필드(response field)
필드	값	설명
구조문_
기본정보	string	구조문_기본정보
법령일련번호	int	법령일련번호
법령ID	int	법령ID
시행일자	int	시행일자
공포일자	int	공포일자
공포번호	int	공포번호
현행여부	string	현행여부
제개정구분명	string	제개정구분명
법령명	string	법령
법종구분	string	법종구분
신조문_
기본정보	string	구조문과 동일한 기본 정보 들어가 있음.
구조문목록	string	구조문목록
조문	string	조문
신조문목록	string	신조문목록
조문	string	조문
신구법
존재여부	string	신구법이 존재하지 않을 경우 N이 조회.


## 3. [일자별 조문 개정 이력 목록 조회 API]
이 서비스는 전일 데이터를 기준으로 제공됩니다. 원하시는 날짜의 익일에 서비스를 조회해주시기 바랍니다.
(예) 2017년10월1일에 개정된 조문을 조회할 경우, 2017년10월2일에 regDt=20171001으로 조회
- 요청 URL : http://www.law.go.kr/DRF/lawSearch.do?target=lsJoHstInf
요청 변수 (request parameter)
요청변수	값	설명
OC	string(필수)	사용자 이메일의 ID(g4c@korea.kr일경우 OC값=g4c)
target	string : lsJoHstInf(필수)	서비스 대상
type	char(필수)	출력 형태 XML/JSON
regDt	int	조문 개정일, 8자리 (20150101)
fromRegDt	int	조회기간 시작일, 8자리 (20150101)
toRegDt	int	조회기간 종료일, 8자리 (20150101)
ID	int	법령ID
JO	int	조문번호
조문번호 4자리 + 조 가지번호 2자리
(000202 : 제2조의2)
org	string	소관부처별 검색(소관부처코드 제공)
page	int	검색 결과 페이지 (default=1)
샘플 URL
1. 조문 개정 일자가 20250401인 조문 XML 검색
http://law.go.kr/DRF/lawSearch.do?target=lsJoHstInf&OC=test&regDt=20250401&type=XML
2. 조문 개정 일자 기간 검색 중 검색 기간 시작일이 20250101인 조문 XML 검색
http://www.law.go.kr/DRF/lawSearch.do?target=lsJoHstInf&OC=test&fromRegDt=20250101&type=XML
3. 조문 개정 일자가 20250401이면서 기관이 보건복지부인 조문 JSON 검색
http://www.law.go.kr/DRF/lawSearch.do?target=lsJoHstInf&OC=test&regDt=20250401&org=1352000&type=JSON
출력 결과 필드(response field)
필드	값	설명
target	string	검색서비스 대상
totalCnt	int	검색한 기간에 개정 조문이 있는 법령의 건수
law id	int	결과 번호
법령일련번호	int	법령일련번호
법령명한글	string	법령명한글
법령ID	int	법령ID
공포일자	int	공포일자
공포번호	int	공포번호
제개정구분명	string	제개정구분명
소관부처명	string	소관부처명
소관부처코드	string	소관부처코드
법령구분명	string	법령구분명
시행일자	int	시행일자
jo num	string	조 구분 번호
조문정보	string	조문정보
조문번호	string	조문번호
변경사유	string	변경사유
조문링크	string	조문링크
조문변경이력
상세링크	string	조문변경이력상세링크
조문개정일	int	조문제개정일
조문시행일	int	조문시행일

## 4. [법령정보지식베이스 법령용어 조회 API]
- 요청 URL : https://www.law.go.kr/DRF/lawSearch.do?target=lstrmAI
법령정보지식베이스 법령용어 조회 API
요청 변수 (request parameter)
요청변수	값	설명
OC	string(필수)	사용자 이메일의 ID
(g4c@korea.kr일경우 OC값=g4c)
target	string(필수)	서비스 대상
(법령용어 : lstrmAI)
type	char(필수)	출력 형태 : XML/JSON
query	string	법령용어명에서 검색을 원하는 질의
display	int	검색된 결과 개수
(default=20 max=100)
page	int	검색 결과 페이지 (default=1)
homonymYn	char	동음이의어 존재여부 (Y/N)
샘플 URL
1. 법령정보지식베이스 법령용어 XML 조회
https://www.law.go.kr/DRF/lawSearch.do?OC=test&target=lstrmAI&type=XML
2. 법령정보지식베이스 법령용어 JSON 조회
https://www.law.go.kr/DRF/lawSearch.do?OC=test&target=lstrmAI&type=JSON
출력 결과 필드(response field)
필드	값	설명
target	string	검색서비스 대상
키워드	string	검색 단어
검색결과개수	int	검색 건수
section	string	검색범위
page	int	현재 페이지번호
numOfRows	int	페이지 당 출력 결과 수
법령용어 id	string	법령용어 순번
법령용어명	string	법령용어명
동음이의어
존재여부	string	동음이의어 존재여부
비고	string	동음이의어 내용
용어간관계
링크	string	법령용어-일상용어 연계 정보 상세링크
조문간관계
링크	string	법령용어-조문 연계 정보 상세링크

## 5. [별표서식 목록 조회 API]
- 요청 URL : http://www.law.go.kr/DRF/lawSearch.do?target=licbyl
요청 변수 (request parameter)
요청변수	값	설명
OC	string(필수)	사용자 이메일의 ID(g4c@korea.kr일경우 OC값=g4c)
target	string : licbyl(필수)	서비스 대상
type	char(필수)	출력 형태 HTML/XML/JSON
search	int	검색범위
(기본 : 1 별표서식명)
2 : 해당법령검색
3 : 별표본문검색
query	string	검색을 원하는 질의(default=*)
(정확한 검색을 위한 문자열 검색 query="자동차")
display	int	검색된 결과 개수 (default=20 max=100)
page	int	검색 결과 페이지 (default=1)
sort	string	정렬옵션 (기본 : lasc 별표서식명 오름차순),
ldes(별표서식명 내림차순)
org	string	소관부처별 검색(소관부처코드 제공)
소관부처 2개이상 검색 가능(","로 구분)
mulOrg	string	소관부처 2개이상 검색 조건
OR : OR검색 (default)
AND : AND검색
knd	string	별표종류
1 : 별표 2 : 서식 3 : 별지 4 : 별도 5 : 부록
gana	string	사전식 검색(ga,na,da…,etc)
popYn	string	상세화면 팝업창 여부(팝업창으로 띄우고 싶을 때만 'popYn=Y')
샘플 URL
1. 법령 별표서식 목록 XML 검색
http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=licbyl&type=XML
2. 법령 별표서식 목록 HTML 검색
http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=licbyl&type=HTML
3. 법령 별표서식 목록 JSON 검색
http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=licbyl&type=JSON
4. 경찰청 법령 별표서식 목록 검색
http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=licbyl&type=XML&org=1320000
5. 소관부처 2개이상(경찰청, 행정안전부) 입력한 별표서식 목록 HTML 검색(OR검색)
http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=licbyl&type=HTML&org=1320000,1741000
6. 소관부처 2개이상(경찰청, 행정안전부) 입력한 별표서식 목록 HTML 검색(AND검색)
http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=licbyl&type=HTML&org=1320000,1741000&mulOrg=AND
출력 결과 필드(response field)
필드	값	설명
target	string	검색서비스 대상
키워드	string	검색어
section	string	검색범위
totalCnt	int	검색건수
page	int	결과페이지번호
licbyl id	int	결과번호
별표일련번호	int	별표일련번호
관련법령일련번호	int	관련법령일련번호
관련법령ID	int	관련법령ID
별표명	string	별표명ID
관련법령명	string	관련법령명
별표번호	int	별표번호
별표종류	string	별표종류
소관부처명	string	소관부처명
공포일자	int	공포일자
공포번호	int	공포번호
제개정구분명	string	제개정구분명
법령종류	string	법령종류
별표서식
파일링크	string	별표서식파일링크
별표서식
PDF파일링크	string	별표서식PDF파일링크
별표법령
상세링크	string	별표법령상세링크

## 6. [변경이력 목록 조회 API]
- 요청 URL : http://www.law.go.kr/DRF/lawSearch.do?target=lsHstInf
요청 변수 (request parameter)
요청변수	값	설명
OC	string(필수)	사용자 이메일의 ID(g4c@korea.kr일경우 OC값=g4c)
target	string : lsHstInf(필수)	서비스 대상
type	char(필수)	출력 형태 HTML/XML/JSON
regDt	int(필수)	법령 변경일 검색(20150101)
org	string	소관부처별 검색(소관부처코드 제공)
display	int	검색된 결과 개수 (default=20 max=100)
page	int	검색 결과 페이지 (default=1)
popYn	string	상세화면 팝업창 여부(팝업창으로 띄우고 싶을 때만 'popYn=Y')
샘플 URL
1. 법령 변경일이 20170726인 법령 HTML 목록
http://www.law.go.kr/DRF/lawSearch.do?target=lsHstInf&OC=test&regDt=20170726&type=HTML
2. 법령 변경일이 20170726인 법령 XML 목록
http://www.law.go.kr/DRF/lawSearch.do?target=lsHstInf&OC=test&regDt=20170726&type=XML
2. 법령 변경일이 20170726인 법령 JSON 목록
http://www.law.go.kr/DRF/lawSearch.do?target=lsHstInf&OC=test&regDt=20170726&type=JSON
출력 결과 필드(response field)
필드	값	설명
target	string	검색서비스 대상
totalCnt	int	검색건수
page	int	현재 페이지번호
law id	int	검색 결과 순번
법령일련번호	int	법령일련번호
현행연혁코드	string	현행연혁코드
법령명한글	string	법령명한글
법령ID	int	법령ID
공포일자	int	공포일자
공포번호	int	공포번호
제개정구분명	string	제개정구분명
소관부처코드	string	소관부처코드
소관부처명	string	소관부처명
법령구분명	string	법령구분명
시행일자	int	시행일자
자법타법여부	string	자법타법여부
법령상세링크	string	법령상세링크

## 7. [맞춤형 법령 목록 조회 API]
- 요청 URL : http://www.law.go.kr/DRF/lawSearch.do?target=couseLs
요청 변수 (request parameter)
요청변수	값	설명
OC	string(필수)	사용자 이메일의 ID(g4c@korea.kr일경우 OC값=g4c)
target	string : couseLs(필수)	서비스 대상
type	char(필수)	출력 형태 : HTML/XML/JSON
vcode	string(필수)	분류코드
법령은 L로 시작하는 14자리 코드(L0000000000001)
display	int	검색된 결과 개수 (default=20 max=100)
page	int	검색 결과 페이지 (default=1)
popYn	string	상세화면 팝업창 여부(팝업창으로 띄우고 싶을 때만 'popYn=Y')
샘플 URL
1. 분류코드가 L0000000003384인 맞춤형 분류 목록 검색
http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=couseLs&type=XML&vcode=L0000000003384
2. 분류코드가 L0000000003384인 맞춤형 분류 목록 HTML 검색
http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=couseLs&type=HTML&vcode=L0000000003384
3. 분류코드가 L0000000003384인 맞춤형 분류 목록 JSON 검색
http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=couseLs&type=JSON&vcode=L0000000003384
출력 결과 필드(response field)
필드	값	설명
target	string	검색서비스 대상
vcode	string	분류코드
section	string	검색범위
totalCnt	int	검색건수
page	int	결과페이지번호
law id	int	결과 번호
법령일련번호	int	법령일련번호
법령명한글	string	법령명한글
법령ID	int	법령ID
공포일자	int	공포일자
공포번호	int	공포번호
제개정구분명	string	제개정구분명
소관부처명	string	소관부처명
소관부처코드	string	소관부처코드
법령구분명	string	법령구분명
시행일자	int	시행일자
법령상세링크	string	법령상세링크

## 8. [법령정보지식베이스 지능형 법령검색 시스템 검색 API]
- 요청 URL : https://www.law.go.kr/DRF/lawSearch.do?target=aiSearch
법령정보지식베이스 지능형 법령검색 시스템 검색 API
요청 변수 (request parameter)
요청변수	값	설명
OC	string(필수)	사용자 이메일의 ID
(g4c@korea.kr일경우 OC값=g4c)
target	string(필수)	서비스 대상
(지능형 법령검색 시스템 검색 API : aiSearch)
type	char(필수)	출력 형태 : XML/JSON
search	int	검색범위 법령분류
(0:법령조문, 1:법령 별표·서식, 2:행정규칙 조문, 3:행정규칙 별표·서식)
query	string	법령명에서 검색을 원하는 질의
(정확한 검색을 위한 문자열 검색 query="뺑소니")
display	int	검색된 결과 개수 (default=20)
page	int	검색 결과 페이지 (default=1)
샘플 URL
1. 법령정보지식베이스 지능형 법령검색 시스템 검색 API XML 조회
https://www.law.go.kr/DRF/lawSearch.do?OC=test&target=aiSearch&type=XML&search=0&query=뺑소니
2. 법령정보지식베이스 지능형 법령검색 시스템 검색 API JSON 조회
https://www.law.go.kr/DRF/lawSearch.do?OC=test&target=aiSearch&type=JSON&search=0&query=뺑소니
출력 결과 필드(response field)
필드	값	설명
target	string	검색서비스 대상
키워드	string	검색 단어
검색결과개수	int	검색 건수
법령조문ID	int	법령조문 ID
법령ID	string	법령ID
법령일련번호	string	법령일련번호
법령명	string	법령명
시행일자	string	법령 시행일자
공포일자	string	법령 공포일자
공포번호	string	법령 공포번호
소관부처코드	string	소관부처코드
소관부처명	string	소관부처명
법령종류명	string	법령종류명
제개정구분명	string	법령 제개정구분명
법령편장절관코드	string	법령편장절관코드
조문일련번호	string	법령 조문일련번호
조문번호	string	법령 조문번호
조문가지번호	string	법령 조문가지번호
조문제목	string	법령 조문제목
조문내용	string	법령 조문내용
법령별표서식
ID	int	법령별표서식 ID
별표서식
일련번호	string	법령 별표서식일련번호
별표서식번호	string	법령 별표서식번호
별표서식
가지번호	string	법령 별표서식가지번호
별표서식제목	string	법령 별표서식제목
별표서식
구분코드	string	법령 별표서식구분코드
별표서식
구분명	string	법령 별표서식구분명
행정규칙조문
ID	int	행정규칙조문 ID
행정규칙
일련번호	string	행정규칙일련번호
행정규칙ID	string	행정규칙ID
행정규칙명	string	행정규칙명
발령일자	string	발령일자
발령번호	string	발령번호
시행일자	string	시행일자
발령기관명	string	발령기관명
행정규칙
종류명	string	행정규칙종류명
제개정구분명	string	행정규칙 제개정구분명
조문일련번호	string	행정규칙 조문일련번호
조문번호	string	행정규칙 조문번호
조문가지번호	string	행정규칙 조문가지번호
조문제목	string	행정규칙 조문제목
조문내용	string	행정규칙 조문내용
행정규칙
별표서식ID	int	행정규칙별표서식 ID
별표서식
일련번호	string	행정규칙 별표서식일련번호
별표서식번호	string	행정규칙 별표서식번호
별표서식
가지번호	string	행정규칙 별표서식가지번호
별표서식제목	string	행정규칙 별표서식제목
별표서식
구분코드	string	행정규칙 별표서식구분코드
별표서식
구분명	string	행정규칙 별표서식구분명

## 9. [법령정보지식베이스 지능형 법령검색 시스템 연관법령 API]

- 요청 URL : https://www.law.go.kr/DRF/lawSearch.do?target=aiRltLs
법령정보지식베이스 지능형 법령검색 시스템 연관법령 API
요청 변수 (request parameter)
요청변수	값	설명
OC	string(필수)	사용자 이메일의 ID
(g4c@korea.kr일경우 OC값=g4c)
target	string(필수)	서비스 대상
(지능형 법령검색 시스템 연관법령 API : aiRltLs)
type	char(필수)	출력 형태 : XML/JSON
search	int	검색범위 법령분류(0:법령조문, 1:행정규칙조문)
query	string	법령명에서 검색을 원하는 질의
(정확한 검색을 위한 문자열 검색 query="뺑소니")
샘플 URL
1. 법령정보지식베이스 지능형 법령검색 시스템 연관법령 API XML 조회
https://www.law.go.kr/DRF/lawSearch.do?OC=test&target=aiRltLs&type=XML&search=0&query=뺑소니
2. 법령정보지식베이스 지능형 법령검색 시스템 연관법령 API JSON 조회
https://www.law.go.kr/DRF/lawSearch.do?OC=test&target=aiRltLs&type=JSON&search=0&query=뺑소니
출력 결과 필드(response field)
필드	값	설명
target	string	검색서비스 대상
키워드	string	검색 단어
검색결과개수	int	검색 건수
법령조문ID	int	법령조문 ID
법령ID	string	법령ID
법령명	string	법령명
시행일자	string	법령 시행일자
공포일자	string	법령 공포일자
공포번호	string	법령 공포번호
조문번호	string	법령 조문번호
조문가지번호	string	법령 조문가지번호
조문제목	string	법령 조문제목
행정규칙조문
ID	int	행정규칙조문 ID
행정규칙ID	string	행정규칙ID
행정규칙명	string	행정규칙명
발령일자	string	발령일자
발령번호	string	발령번호
조문번호	string	행정규칙 조문번호
조문가지번호	string	행정규칙 조문가지번호
조문제목	string	행정규칙 조문제목

## 10. [판례 본문 조회 API]
- 요청 URL : http://www.law.go.kr/DRF/lawService.do?target=prec
요청 변수 (request parameter)
요청변수	값	설명
OC	string(필수)	사용자 이메일의 ID(g4c@korea.kr일경우 OC값=g4c)
target	string : prec(필수)	서비스 대상
type	char(필수)	출력 형태 : HTML/XML/JSON
*국세청 판례 본문 조회는 HTML만 가능합니다
ID	char(필수)	판례 일련번호
LM	string	판례명
샘플 URL
1. 판례일련번호가 228541인 판례 HTML 조회
http://www.law.go.kr/DRF/lawService.do?OC=test&target=prec&ID=228541&type=HTML
2. 판례일련번호가 228541인 판례 XML 조회
http://www.law.go.kr/DRF/lawService.do?OC=test&target=prec&ID=228541&type=XML
3. 판례일련번호가 228541인 판례 JSON 조회
http://www.law.go.kr/DRF/lawService.do?OC=test&target=prec&ID=228541&type=JSON
출력 결과 필드(response field)
필드	값	설명
판례정보일련번호	int	판례정보일련번호
사건명	string	사건명
사건번호	string	사건번호
선고일자	int	선고일자
선고	string	선고
법원명	string	법원명
법원종류코드	int	법원종류코드(대법원:400201, 하위법원:400202)
사건종류명	string	사건종류명
사건종류코드	int	사건종류코드
판결유형	string	판결유형
판시사항	string	판시사항
판결요지	string	판결요지
참조조문	string	참조조문
참조판례	string	참조판례
판례내용	string	판례내용

## 12. [판례 목록 조회 API]
판례 목록 조회 API
- 요청 URL : http://www.law.go.kr/DRF/lawSearch.do?target=prec
요청 변수 (request parameter)
요청변수	값	설명
OC	string(필수)	사용자 이메일의 ID(g4c@korea.kr일경우 OC값=g4c)
target	string : prec(필수)	서비스 대상
type	char(필수)	출력 형태 : HTML/XML/JSON
search	int	검색범위 (기본 : 1 판례명) 2 : 본문검색
query	string	검색범위에서 검색을 원하는 질의(검색 결과 리스트)
(정확한 검색을 위한 문자열 검색 query="자동차")
display	int	검색된 결과 개수 (default=20 max=100)
page	int	검색 결과 페이지 (default=1)
org	string	법원종류 (대법원:400201, 하위법원:400202)
curt	string	법원명 (대법원, 서울고등법원, 광주지법, 인천지방법원)
JO	string	참조법령명(형법, 민법 등)
gana	string	사전식 검색(ga,na,da…,etc)
sort	string	정렬옵션
lasc : 사건명 오름차순
ldes : 사건명 내림차순
dasc : 선고일자 오름차순
ddes : 선고일자 내림차순(생략시 기본)
nasc : 법원명 오름차순
ndes : 법원명 내림차순
date	int	판례 선고일자
prncYd	string	선고일자 검색(20090101~20090130)
nb	string	판례 사건번호
datSrcNm	string	데이터출처명
(국세법령정보시스템, 근로복지공단산재판례, 대법원)
popYn	string	상세화면 팝업창 여부(팝업창으로 띄우고 싶을 때만 'popYn=Y')
샘플 URL
1. 사건명에 '담보권'이 들어가는 판례 목록 XML 검색
http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=prec&type=XML&query=담보권
2. 사건명에 '담보권'이 들어가고 법원이 '대법원'인 판례 목록 HTML 검색
http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=prec&type=HTML&query=담보권&curt=대법원
3. 사건번호가 '2009느합133,2010느합21' 인 판례 목록 HTML 검색
http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=prec&type=HTML&nb=2009느합133,2010느합21
4. 데이터출처가 근로복지공단산재판례인 판례 목록 JSON 검색
http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=prec&type=JSON&datSrcNm=근로복지공단산재판례
출력 결과 필드(response field)
필드	값	설명
target	string	검색 대상
공포번호	string	공포번호
키워드	string	검색어
section	string	검색범위(EvtNm:판례명/bdyText:본문)
totalCnt	int	검색결과갯수
page	int	출력페이지
prec id	int	검색결과번호
판례일련번호	int	판례일련번호
사건명	string	사건명
사건번호	string	사건번호
선고일자	string	선고일자
법원명	string	법원명
법원종류코드	int	법원종류코드(대법원:400201, 하위법원:400202)
사건종류명	string	사건종류명
사건종류코드	int	사건종류코드
판결유형	string	판결유형
선고	string	선고
데이터출처명	string	데이터출처명
판례상세링크	string	판례상세링크

## 13. [제목]
(내용 붙여넣기)

## 14. [제목]
(내용 붙여넣기)

