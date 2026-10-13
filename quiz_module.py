import os
import re
import json
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from dotenv import load_dotenv

load_dotenv()

def clean_json_block(text: str) -> str:
    cleaned = re.sub(r"```(?:json)?\s*(.*?)\s*```", r"\1", text, flags=re.DOTALL).strip()
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start != -1 and end != -1 and end > start:
        return cleaned[start : end + 1]
    return cleaned

def generate_quiz(text: str) -> list:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key.strip())

            prompt = f"""You are a quiz generator.

From the following passage or topic, create 3 multiple-choice questions. Each question should include:
- A "question" string
- A list of 4 "options" strings
- A correct "answer" string that must exactly match one of the options.

Format your output as **valid JSON**, like this:
[
  {{
    "question": "What is ...?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "Option A"
  }}
]

Passage:
{text}
"""
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
                    quiz_text = response.text.strip()
                    cleaned_text = clean_json_block(quiz_text)
                    parsed_quiz = json.loads(cleaned_text)
                    if isinstance(parsed_quiz, list) and len(parsed_quiz) > 0:
                        return parsed_quiz
                except Exception:
                    continue
        except Exception as e:
            print(f"Quiz generation error: {e}")

    # Fallback interactive quiz
    topic_clean = text.strip()
    return [
        {
            "question": f"What is the primary foundation or concept behind {topic_clean}?",
            "options": [
                f"Core principles and mechanisms of {topic_clean}",
                "Unrelated theoretical assumptions",
                "Arbitrary random variables",
                "Historical trivia without practical relevance"
            ],
            "answer": f"Core principles and mechanisms of {topic_clean}"
        },
        {
            "question": f"How is {topic_clean} typically applied in modern learning and practice?",
            "options": [
                "Only through physical hand calculations",
                f"By analyzing structured patterns and applying {topic_clean} systematically",
                "By ignoring edge cases and prerequisites",
                "Exclusively in isolated laboratory simulations"
            ],
            "answer": f"By analyzing structured patterns and applying {topic_clean} systematically"
        },
        {
            "question": f"Which of the following best describes an essential benefit of studying {topic_clean}?",
            "options": [
                "It eliminates the need for problem-solving skills",
                "It requires memorizing formulas without understanding",
                f"It builds deeper analytical understanding of {topic_clean}",
                "It has no real-world application"
            ],
            "answer": f"It builds deeper analytical understanding of {topic_clean}"
        }
    ]
