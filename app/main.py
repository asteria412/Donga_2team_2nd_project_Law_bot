# app/main.py
from fastapi import FastAPI
from api.law_versions import router as law_router
# You can easily import from your other folders here:
# from app.agent.bot_logic import process_question

app = FastAPI(title="Law Bot System")

# Connect your API components
app.include_router(law_router, prefix="/api")

@app.get("/")
def home():
    return {"message": "Law Bot System is Active"}

# Example of using another folder:
@app.post("/ask")
def ask_the_bot(question: str):
    # logic from app.agent.bot_logic
    return {"answer": "The law says..."}