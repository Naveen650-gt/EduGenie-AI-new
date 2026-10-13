import os
import threading
from dotenv import load_dotenv

load_dotenv()

# Global holders for local Hugging Face model and tokenizer (optional if torch/transformers are installed)
_explain_tokenizer = None
_explain_model = None
_is_downloading = False
_model_lock = threading.Lock()
_model_name = "MBZUAI/LaMini-Flan-T5-783M"

def _load_model_worker():
    global _explain_tokenizer, _explain_model, _is_downloading
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        import torch

        print(f"EduGenie: Downloading/loading local model {_model_name} in background...")
        tokenizer = AutoTokenizer.from_pretrained(_model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(_model_name)
        model.eval()

        with _model_lock:
            _explain_tokenizer = tokenizer
            _explain_model = model
            _is_downloading = False
        print(f"EduGenie: Local model {_model_name} is now loaded and ready for offline inference!")
    except Exception as e:
        print(f"EduGenie: Note regarding local model loading ({_model_name}): {e}")
        with _model_lock:
            _is_downloading = False

def _get_local_model():
    global _explain_tokenizer, _explain_model, _is_downloading
    with _model_lock:
        if _explain_model is not None and _explain_tokenizer is not None:
            return _explain_tokenizer, _explain_model

    # Check if transformers & torch are installed in environment
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        tokenizer = AutoTokenizer.from_pretrained(_model_name, local_files_only=True)
        model = AutoModelForSeq2SeqLM.from_pretrained(_model_name, local_files_only=True)
        model.eval()
        with _model_lock:
            _explain_tokenizer = tokenizer
            _explain_model = model
        return tokenizer, model
    except ModuleNotFoundError:
        # Running in lightweight/cloud environment (e.g. Vercel Serverless)
        return None, None
    except Exception:
        # Not cached locally; start background download thread if available
        try:
            import transformers
            with _model_lock:
                if not _is_downloading:
                    _is_downloading = True
                    t = threading.Thread(target=_load_model_worker, daemon=True)
                    t.start()
        except ImportError:
            pass
        return None, None

def explain_topic(topic: str) -> str:
    """
    Explains a concept in a simple, readable way for a school student.
    Uses local model when torch/transformers are installed, with fast Gemini cloud execution.
    """
    input_text = f"Explain the concept of '{topic}' in a simple and clear way for a school student."

    # 1. Try local LaMini-Flan-T5 model if supported in environment
    tokenizer, model = _get_local_model()
    if tokenizer is not None and model is not None:
        try:
            inputs = tokenizer(input_text, return_tensors="pt")
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.7,
                top_k=50,
                top_p=0.95,
                do_sample=True
            )
            explanation = tokenizer.decode(outputs[0], skip_special_tokens=True)
            if explanation and len(explanation.strip()) > 5:
                return explanation.strip()
        except Exception as e:
            print(f"Local inference warning: {e}. Falling back to cloud LLM.")

    # 2. Cloud Gemini execution (Default for Vercel Serverless & cloud deploys)
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key.strip())
            for m_name in [
                "gemini-3.5-flash",
                "models/gemini-3.5-flash",
                "gemini-3.8-flash",
                "gemini-1.5-flash",
                "gemini-1.5-pro"
            ]:
                try:
                    model = genai.GenerativeModel(model_name=m_name)
                    res = model.generate_content(input_text)
                    if hasattr(res, "text") and res.text:
                        return res.text.strip()
                except Exception:
                    continue
        except Exception as e:
            print(f"Gemini fallback warning: {e}")

    # 3. Informative explanation preview
    return (
        f"**Concept: {topic}**\n\n"
        f"In simple terms, {topic} is a key concept that helps us understand how components work together step-by-step. "
        f"Just like solving a puzzle, {topic} provides clear rules and patterns so that complex problems become easy to manage.\n\n"
        f"*(Configure GEMINI_API_KEY in Vercel Environment Variables to enable live AI responses!)*"
    )
