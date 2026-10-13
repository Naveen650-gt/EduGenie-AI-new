import os
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from dotenv import load_dotenv

load_dotenv()

def summarize_text(text: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
        if len(sentences) > 2:
            return " • " + "\n • ".join(sentences[:3]) + "."
        return f"Summary preview: {text[:200]}..."

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key.strip())
        prompt = f"Summarize the following text in simple language:\n\n{text}"

        for model_name in [
            "gemini-3.5-flash",
            "models/gemini-3.5-flash",
            "gemini-3.8-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro"
        ]:
            try:
                model = genai.GenerativeModel(model_name=model_name)
                response = model.generate_content(prompt, request_options={"timeout": 20})
                if hasattr(response, "text") and response.text:
                    return response.text.strip()
            except Exception:
                continue

        return "⚠️ Error: Unable to generate summary with current Gemini models."
    except Exception as e:
        return f"⚠️ Error in Summary: {e}"
