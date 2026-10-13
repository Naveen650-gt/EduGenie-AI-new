import os
import traceback
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from dotenv import load_dotenv

load_dotenv()

def get_learning_recommendations(topic: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return f"""## Learning Recommendations for "{topic}":
### Zero to Mastery Path

**Level 1: Beginner Level (Estimated Time: 1–2 weeks)**
• **Key Topics:** Fundamentals of {topic}, Core Syntax & Concepts, Basic Setup.
• **Resources:** Official Documentation, FreeCodeCamp, YouTube Beginners Crash Course.

**Level 2: Intermediate Level (Estimated Time: 2–3 weeks)**
• **Key Topics:** Real-world problem solving, Practical workflows, Handling edge cases in {topic}.
• **Resources:** LeetCode / HackerRank / GitHub sample projects.

**Level 3: Advanced Level (Estimated Time: 3–4 weeks)**
• **Key Topics:** Performance optimization, Architecture design, Production deployment.
• **Resources:** Advanced textbooks, Research papers, Community forums.
"""

    prompt = f"""You are an AI tutor. The student wants to learn about: {topic}.
Suggest a structured and adaptive learning path including key topics, order of learning, and resources (books, videos, platforms).
Include beginner, intermediate, and advanced levels if needed.
"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key.strip())

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
                    return response.text
                elif hasattr(response, "parts") and response.parts:
                    return "".join(part.text for part in response.parts)
            except Exception:
                continue

        return "❌ Could not extract content from Gemini response."
    except Exception as e:
        traceback.print_exc()
        return f"❌ Error occurred: {str(e)}"
