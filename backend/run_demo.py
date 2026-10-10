"""Run an isolated, offline demo without loading real provider or database keys."""
import os
import secrets
from pathlib import Path

for key in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_JWT_SECRET", "GROQ_API_KEY",
            "GEMINI_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY"):
    os.environ[key] = ""
os.environ["DATA_DIR"] = str(Path(__file__).parent / "data" / "demo")
os.environ["ALLOW_DEMO"] = "true"
demo_dir = Path(os.environ["DATA_DIR"])
demo_dir.mkdir(parents=True, exist_ok=True)
secret_file = demo_dir / ".session-secret"
if not secret_file.exists():
    secret_file.write_text(secrets.token_urlsafe(48), encoding="utf-8")
os.environ["DEMO_SESSION_SECRET"] = secret_file.read_text(encoding="utf-8").strip()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8010)
