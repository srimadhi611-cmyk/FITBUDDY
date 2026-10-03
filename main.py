"""FitBuddy – AI Fitness Plan Generator"""
import os
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from services.gemini_service import generate_plan

load_dotenv()
APP_NAME = os.getenv("APP_NAME", "FitBuddy")
BASE = Path(__file__).resolve().parent

app = FastAPI(title=APP_NAME)
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE / "templates"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "app_name": APP_NAME})


@app.post("/generate-plan", response_class=HTMLResponse)
async def plan(
    request: Request,
    goal: str = Form(...),
    level: str = Form("beginner"),
    equipment: str = Form("home"),
    diet: str = Form("vegetarian"),
    days: int = Form(4),
    notes: str = Form(""),
):
    profile = {
        "goal": goal, "level": level, "equipment": equipment,
        "diet": diet, "days": days, "notes": notes,
    }
    result = generate_plan(profile)
    return templates.TemplateResponse("plan.html", {
        "request": request, "app_name": APP_NAME, "result": result, "profile": profile
    })


@app.get("/health")
async def health():
    return {"status": "ok", "app": APP_NAME, "gemini": bool(os.getenv("GEMINI_API_KEY"))}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=os.getenv("HOST", "0.0.0.0"),
                port=int(os.getenv("PORT", 8000)), reload=True)
