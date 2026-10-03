"""FitBuddy – Gemini service for workout & meal plans."""
import os, json
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
MODEL = "gemini-2.5-pro"


def _parse(text: str):
    text = text.strip()
    if "```json" in text:
        s = text.find("```json") + 7
        e = text.find("```", s)
        text = text[s:e].strip()
    elif "```" in text:
        s = text.find("```") + 3
        e = text.find("```", s)
        text = text[s:e].strip()
    try:
        return json.loads(text)
    except Exception:
        start, end = text.find("{"), text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except Exception:
                pass
        return None


def generate_plan(profile: dict) -> dict:
    goal = profile.get("goal", "general fitness")
    level = profile.get("level", "beginner")
    equipment = profile.get("equipment", "home")
    diet = profile.get("diet", "vegetarian")
    days = int(profile.get("days", 4))
    notes = profile.get("notes", "")

    prompt = f"""You are FitBuddy, a certified fitness coach AI.
Create a safe {days}-day workout + meal suggestion plan.

Profile:
- Goal: {goal}
- Level: {level}
- Equipment: {equipment}
- Diet: {diet}
- Notes: {notes or "None"}

Respond ONLY with JSON:
{{
  "goal": "{goal}",
  "level": "{level}",
  "days": [
    {{
      "day": 1,
      "focus": "e.g. Full body",
      "exercises": [
        {{"name": "Squats", "sets": "3x12", "tip": "Keep back straight"}}
      ],
      "duration_minutes": 40
    }}
  ],
  "meals": [
    {{"name": "Meal idea", "when": "Breakfast/Lunch/Dinner", "notes": "simple tip"}}
  ],
  "recovery_tips": ["tip1", "tip2"],
  "safety_note": "Consult a doctor before starting any new program."
}}
"""
    if not API_KEY:
        return _fallback(profile)
    try:
        model = genai.GenerativeModel(MODEL)
        r = model.generate_content(prompt)
        data = _parse(r.text) or _fallback(profile)
        data["generated_at"] = datetime.utcnow().isoformat() + "Z"
        data["is_fallback"] = False
        return data
    except Exception as e:
        d = _fallback(profile)
        d["error"] = str(e)
        return d


def _fallback(profile: dict) -> dict:
    days = int(profile.get("days", 4))
    day_list = []
    focuses = ["Full body", "Cardio & core", "Upper body", "Lower body", "Active recovery", "Strength", "Flexibility"]
    for d in range(1, days + 1):
        day_list.append({
            "day": d,
            "focus": focuses[(d - 1) % len(focuses)],
            "exercises": [
                {"name": "Bodyweight Squats", "sets": "3x12", "tip": "Knees track over toes"},
                {"name": "Push-ups (or knee push-ups)", "sets": "3x10", "tip": "Core tight"},
                {"name": "Plank", "sets": "3x30s", "tip": "Straight line head to heels"},
            ],
            "duration_minutes": 35 + d * 2,
        })
    return {
        "goal": profile.get("goal", "general fitness"),
        "level": profile.get("level", "beginner"),
        "days": day_list,
        "meals": [
            {"name": "Oats + fruit", "when": "Breakfast", "notes": "Complex carbs for energy"},
            {"name": "Dal + rice + salad", "when": "Lunch", "notes": "Protein + fibre"},
            {"name": "Veg stir-fry + chapati", "when": "Dinner", "notes": "Light evening meal"},
        ],
        "recovery_tips": ["Sleep 7–8 hours", "Drink water", "Stretch after workouts"],
        "safety_note": "Demo plan — set GEMINI_API_KEY for personalised AI plans. Consult a doctor if needed.",
        "is_fallback": True,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
