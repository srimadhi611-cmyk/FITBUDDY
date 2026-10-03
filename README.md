# FitBuddy – AI Fitness Plan Generator

Personalised **workout + meal plans** from your goals using Google Gemini.

## Run (Windows)

```cmd
cd FitBuddy
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Set `GEMINI_API_KEY` in `.env`, then:

```cmd
python main.py
```

http://127.0.0.1:8000

Demo plans work without API key. Not medical advice.
