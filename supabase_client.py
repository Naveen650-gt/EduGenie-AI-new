import os
import sqlite3
import json
import threading
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY")

_supabase_client = None
_client_lock = threading.Lock()
_remote_table_available = None
LOCAL_DB_PATH = "edugenie_local.db"

def _init_local_db():
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS local_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT,
                module_type TEXT,
                prompt_text TEXT,
                response_text TEXT,
                metadata TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS local_quiz_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT,
                topic TEXT,
                score INTEGER,
                total_questions INTEGER,
                percentage REAL
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"EduGenie: Local DB initialization warning: {e}")

_init_local_db()

def get_supabase_client():
    global _supabase_client
    with _client_lock:
        if _supabase_client is not None:
            return _supabase_client

        if not SUPABASE_URL or not SUPABASE_KEY:
            return None

        try:
            from supabase import create_client
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
            return _supabase_client
        except Exception as e:
            print(f"EduGenie: Could not connect to Supabase: {e}")
            return None

def check_supabase_table_exists():
    global _remote_table_available
    client = get_supabase_client()
    if not client:
        return False

    try:
        client.table("edugenie_history").select("id").limit(1).execute()
        _remote_table_available = True
        return True
    except Exception:
        _remote_table_available = False
        return False

def log_interaction(module_type: str, prompt_text: str, response_text: str, metadata: dict = None):
    """
    Asynchronously logs an interaction (Q&A, explanation, quiz, summary, roadmap)
    to Supabase with local SQLite fallback.
    """
    def _worker():
        nonlocal metadata
        if metadata is None:
            metadata = {}

        now_iso = datetime.utcnow().isoformat() + "Z"
        resp_str = str(response_text) if not isinstance(response_text, str) else response_text

        # 1. Try Supabase
        client = get_supabase_client()
        saved_remote = False
        if client:
            try:
                data = {
                    "module_type": module_type,
                    "prompt_text": prompt_text,
                    "response_text": resp_str,
                    "metadata": metadata
                }
                client.table("edugenie_history").insert(data).execute()
                saved_remote = True
            except Exception:
                saved_remote = False

        # 2. Local fallback / backup
        try:
            conn = sqlite3.connect(LOCAL_DB_PATH)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO local_history (created_at, module_type, prompt_text, response_text, metadata) VALUES (?, ?, ?, ?, ?)",
                (now_iso, module_type, prompt_text, resp_str, json.dumps(metadata))
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Local storage note: {e}")

    threading.Thread(target=_worker, daemon=True).start()

def record_quiz_score(topic: str, score: int, total_questions: int):
    """
    Records student score after completing a quiz.
    """
    def _worker():
        pct = round((score / max(1, total_questions)) * 100, 2)
        now_iso = datetime.utcnow().isoformat() + "Z"

        # Try Supabase
        client = get_supabase_client()
        if client:
            try:
                data = {
                    "topic": topic,
                    "score": score,
                    "total_questions": total_questions
                }
                client.table("quiz_scores").insert(data).execute()
            except Exception:
                pass

        # Local backup
        try:
            conn = sqlite3.connect(LOCAL_DB_PATH)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO local_quiz_scores (created_at, topic, score, total_questions, percentage) VALUES (?, ?, ?, ?, ?)",
                (now_iso, topic, score, total_questions, pct)
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    threading.Thread(target=_worker, daemon=True).start()

def get_recent_history(limit: int = 15):
    """
    Fetches the latest learning history from Supabase, or falls back to local SQLite.
    """
    client = get_supabase_client()
    if client:
        try:
            res = client.table("edugenie_history").select("*").order("created_at", desc=True).limit(limit).execute()
            if res.data and len(res.data) > 0:
                return {"source": "supabase", "data": res.data}
        except Exception:
            pass

    # Fallback to local SQLite history
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id, created_at, module_type, prompt_text, response_text, metadata FROM local_history ORDER BY id DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return {"source": "local_cache", "data": rows}
    except Exception as e:
        return {"source": "error", "data": [], "error": str(e)}

def get_status_info():
    """
    Returns connection and table status for frontend badge and diagnostic info.
    """
    has_keys = bool(SUPABASE_URL and SUPABASE_KEY)
    has_client = get_supabase_client() is not None
    table_ok = check_supabase_table_exists()
    return {
        "configured": has_keys,
        "connected": has_client,
        "table_created": table_ok,
        "url": SUPABASE_URL
    }
