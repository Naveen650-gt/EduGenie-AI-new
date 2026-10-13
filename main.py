import os
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, set_key

load_dotenv()

from qna import answer_question_with_gemini
from explanation_module import explain_topic
from summary_module import summarize_text
from quiz_module import generate_quiz
from learning_path import get_learning_recommendations
from supabase_client import (
    log_interaction,
    record_quiz_score,
    get_recent_history,
    get_status_info
)

app = FastAPI(title="EduGenie: Google Gemini Powered Learning Assistant")

# Enable CORS for flexible integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static and templates directories exist
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    has_api_key = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"has_api_key": has_api_key}
    )

# Supabase diagnostic and history endpoints
@app.get("/api/supabase/status")
async def supabase_status():
    return get_status_info()

@app.get("/api/history")
async def get_history(limit: int = 15):
    return get_recent_history(limit=limit)

@app.post("/api/quiz/record-score")
async def record_score(request: Request):
    data = await request.json()
    topic = data.get("topic", "General Quiz")
    score = int(data.get("score", 0))
    total = int(data.get("total", 3))
    record_quiz_score(topic, score, total)
    return {"success": True, "message": "Score saved successfully"}

# Key management endpoints
@app.get("/api/key-status")
async def key_status():
    has_key = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    return {"has_key": has_key}

@app.post("/api/set-key")
async def save_api_key(request: Request):
    data = await request.json()
    key = data.get("key", "").strip()
    if not key:
        return JSONResponse(content={"error": "Key cannot be empty."}, status_code=400)
    
    os.environ["GEMINI_API_KEY"] = key
    env_file = ".env"
    try:
        set_key(env_file, "GEMINI_API_KEY", key)
    except Exception:
        with open(env_file, "a") as f:
            f.write(f"\nGEMINI_API_KEY={key}\n")
    return {"success": True, "message": "API key successfully configured!"}

# Q&A - GET API using Gemini
@app.get("/qa")
async def answer_question(question: str = Query(...)):
    answer = answer_question_with_gemini(question)
    log_interaction("qa", question, answer)
    return {"answer": answer}

# Explanation - POST API (Local LaMini-Flan-T5 with Gemini fallback)
@app.post("/explain")
async def explain_api(request: Request):
    data = await request.json()
    topic = data.get("topic")
    if not topic:
        return JSONResponse(content={"error": "Please provide a topic."}, status_code=400)
    explanation = explain_topic(topic)
    log_interaction("explain", topic, explanation)
    return {"topic": topic, "explanation": explanation}

# Summarization - POST API
@app.post("/summarize")
async def summarize_api(request: Request):
    data = await request.json()
    text = data.get("text")
    if not text:
        return JSONResponse(content={"error": "Please provide text to summarize."}, status_code=400)
    summary = summarize_text(text)
    log_interaction("summarize", text[:300] + "...", summary)
    return {"summary": summary}

# Quiz Generation - POST API
@app.post("/quiz")
async def quiz_api(request: Request):
    data = await request.json()
    text = data.get("text")
    if not text:
        return JSONResponse(content={"error": "Please provide text for quiz."}, status_code=400)
    quiz = generate_quiz(text)
    log_interaction("quiz", text, f"Generated {len(quiz)} questions", {"questions_count": len(quiz)})
    return JSONResponse(content={"quiz": quiz})

# Learning Recommendations - GET API
@app.get("/learn/recommendations")
async def learning_recommendation_api(topic: str = Query(...)):
    recommendation = get_learning_recommendations(topic)
    log_interaction("roadmap", topic, recommendation)
    return {"topic": topic, "recommendation": recommendation}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
