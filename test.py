import os
import json
import urllib.error
import urllib.request

key_before = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_TOKEN")
try:
    from dotenv import load_dotenv

    load_dotenv(override=False)
except Exception:
    pass

key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_TOKEN")
if key:
    if key_before:
        print("using GROQ_API_KEY from shell env")
    else:
        print("using GROQ_API_KEY from .env")
if not key:
    print("GROQ_API_KEY not set")
    raise SystemExit(1)

payload = {
    "model": "llama-3.1-8b-instant",
    "messages": [{"role": "user", "content": "hi"}],
}
req = urllib.request.Request(
    "https://api.groq.com/openai/v1/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "User-Agent": "curl/8.0",
    },
)

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        if resp.status == 200:
            print("success: Groq API key works")
        else:
            print(resp.status)
except urllib.error.HTTPError as exc:
    body = exc.read().decode("utf-8", errors="replace")
    print(exc.code)
    if body:
        print(body)
except Exception as exc:
    print(f"error: {exc}")
