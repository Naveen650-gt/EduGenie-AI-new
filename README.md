# EduGenie: Google Gemini Powered Learning Assistant 💡

EduGenie is a lightweight AI-powered educational assistant designed for students and educators. It combines **cloud-based intelligence (Google Gemini)** for complex reasoning with **local edge intelligence (MBZUAI/LaMini-Flan-T5-783M)** for lightweight, low-footprint educational concept explanations.

---

## 🌟 Features

1. **Ask EduGenie a Question (Q&A)**
   - Answers general knowledge and academic questions accurately using Google Gemini.
   - Endpoint: `GET /qa?question=...`

2. **Need an Explanation? (Concept Explanations)**
   - Simplifies complex topics into school-student friendly explanations using the local instruction-tuned `MBZUAI/LaMini-Flan-T5-783M` model (with cloud fallback).
   - Endpoint: `POST /explain` with body `{"topic": "Photosynthesis"}`

3. **Summarize a Paragraph**
   - Condenses long educational passages and articles into concise, revision-ready bullet points.
   - Endpoint: `POST /summarize` with body `{"text": "..."}`

4. **Interactive Quiz Generator**
   - Generates 3 multiple-choice questions (MCQs) with 4 options each, formatted in structured JSON.
   - Includes real-time client-side interactive answer evaluation (`✔ Correct!` / `❌ Incorrect`).
   - Endpoint: `POST /quiz` with body `{"text": "Pythagoras theorem"}`

5. **Personalized Learning Path Recommendations**
   - Generates structured, adaptive curriculums from beginner to advanced with estimated timelines, learning topics, and curated resources (books, videos, docs).
   - Endpoint: `GET /learn/recommendations?topic=SQL`

---

## 📁 Project Structure

```
EduGenie/
├── main.py                     # FastAPI application & REST API routes
├── explanation_module.py       # Local LaMini-Flan-T5 model inference logic
├── qna.py                      # Gemini Q&A logic
├── quiz_module.py              # MCQ quiz generation & JSON parser
├── summary_module.py           # Text summarization pipeline
├── learning_path.py            # Personalized curriculum recommendation generator
├── templates/
│   └── index.html              # Modern, responsive web frontend
├── static/
│   └── style.css               # Clean stylesheet matching project specification
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (Gemini API Key)
├── .env.example                # Template for environment variables
└── run.bat                     # Windows 1-click startup script
```

---

## 🚀 Getting Started

### 1. Requirements & Setup
All dependencies (`fastapi`, `uvicorn`, `jinja2`, `torch`, `transformers`, `google-generativeai`, `python-dotenv`) are installed.

If you ever need to reinstall:
```bash
py -m pip install -r requirements.txt
```

### 2. Configure Your Gemini API Key
To get free API access:
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Generate an API key.
3. Add it to `.env`:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```
*(You can also set it directly in the web UI using the **"⚙️ Configure API Key"** button).*

### 3. Run the Application

#### Option A: One-click Batch File
Double-click `run.bat` or run:
```powershell
.\run.bat
```

#### Option B: Terminal Command
```powershell
py -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Access the Web Application
Open your browser and navigate to:
```
http://127.0.0.1:8000
```
API Documentation (Swagger UI) is available at:
```
http://127.0.0.1:8000/docs
```
