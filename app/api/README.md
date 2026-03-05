## API 서버 실행
```
cd app
\Donga_2team_2nd_project_Law_bot\app>python -m uvicorn main:app --reload
```
## API 사용 예시 

### 신구법 변화 목록 조회(법령명 등으로 검색)
/api/law-versions/?name={구체적인 법령명 키워드}&mst={구체적인 법령일련번호}

예시:
/api/law-versions/?name="부가가치세법"&mst=283641

### 신구법 변화 본문 조회(하나의 법령 ID에 해당되는 변화 본문 조회)
/api/law-versions/{법령ID}/comparison

예시:
/api/law-versions/001571/comparison

## 도메인 개념
MST (법령일련번호): 법 개정시에 생성되고 할당되는 번호
Law ID (법령ID): 법 자체를 가리키므로 개정시에도 유지되고 신구법을 연관시킬 수 있는 번호
