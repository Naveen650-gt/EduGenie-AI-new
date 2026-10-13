import os
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from dotenv import load_dotenv

load_dotenv()

def get_genai():
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key.strip())
        return genai, api_key.strip()
    return None, None

def answer_question_with_gemini(question: str) -> str:
    genai, api_key = get_genai()
    if not api_key:
        return (
            "⚠️ Gemini API Key not found. Please set your GEMINI_API_KEY in the .env file "
            "or enter it in the top settings banner."
        )

    # Models prioritized by speed and current availability
    model_names = [
        "gemini-3.5-flash",
        "models/gemini-3.5-flash",
        "gemini-3.8-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]
    last_err = None

    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name=model_name)
            response = model.generate_content(question, request_options={"timeout": 20})
            if hasattr(response, "text") and response.text:
                return response.text.strip()
            elif hasattr(response, "parts") and response.parts:
                return "".join(part.text for part in response.parts).strip()
        except Exception as e:
            last_err = e
            continue

    return f"⚠️ Error in QnA: {last_err}"
