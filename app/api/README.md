## API 서버 실행
cd app
\Donga_2team_2nd_project_Law_bot\app>python -m uvicorn main:app --reload
## API 사용 예시
/api/law-versions/?name="부가가치세법"&mst=283641
/api/law-versions/283641/details