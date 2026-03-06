# app/main.py
from fastapi import APIRouter, FastAPI, HTTPException
from api.law_versions import router as law_router
# You can easily import from your other folders here:
# from app.agent.bot_logic import process_question

from enum import Enum

class Team(Enum):
    HR = "인사"
    FINANCE = "재무"
    GENERAL_AFFAIRS = "총무"

# Mapping team to their respective sets of laws
TEAM_LAWS: dict[Team, set[str]] = {
    Team.HR: {
        "근로기준법", 
        "산업안전보건법", 
        "남녀고용평등법"
    },
    Team.FINANCE: {
        "상법", 
        "법인세법", 
        "조세특례제한법", 
        "자본시장과 금융투자업에 관한 법률", 
        "부가가치세법"
    },
    Team.GENERAL_AFFAIRS: {
        "공정거래법", 
        "개인정보보호법", 
        "부가가치세법", 
        "상법"
    }
}

app = FastAPI(title="Law Bot System")

api_router = APIRouter()

# --- 3. Include the law router INTO the api_router ---
# This makes law_router routes available at /api/laws/...
api_router.include_router(law_router)

@api_router.get("/team-laws")
def get_team_laws():
    return {"team_laws": TEAM_LAWS}

@api_router.get("/team-laws/{team_name}")
def get_laws_for_team(team_name: str):
    try:
        team = Team(team_name)
        return {"team": team.value, "laws": list(TEAM_LAWS[team])}
    except ValueError:
        raise HTTPException(status_code=404, detail="Team not found")
    
@api_router.get("/teams")
def get_teams():
    return {"teams": [team.value for team in Team]}

# Example of using another folder:
@api_router.post("/ask")
def ask_the_bot(question: str):
    # logic from app.agent.bot_logic
    return {"answer": "The law says..."}

@api_router.get("/")
def home():
    return {"message": "Law Bot System API is Active"}

app.include_router(api_router, prefix="/api")

