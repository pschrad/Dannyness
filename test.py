from dotenv import load_dotenv  # Load .env files (requires python-dotenv).
import os  # Read environment variables.
import json  # Encode JSON payloads.
import urllib.error  # Handle HTTP errors.
import urllib.request  # Make HTTP requests.
from createprompt import get_prompt  # Load prompt from a separate module.
#print(os.environ)
key_before = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_TOKEN")  # Check shell env first.
load_dotenv(override=False)  # Don't override existing shell env vars.

key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_TOKEN")  # Read the API key.
if key:
    if key_before:
        print("using GROQ_API_KEY from shell env")  # Let the user know the source.
    else:
        print("using GROQ_API_KEY from .env")  # Let the user know the source.
if not key:
    print("GROQ_API_KEY not set")  # Missing key message.
    raise SystemExit(1)  # Stop the script if no key.

prompt = get_prompt()  # Read prompt from createprompt.py.
if not prompt:
    print("No prompt provided")
    raise SystemExit(1)

payload = {  # Minimal chat request body.
    "model": "llama-3.1-8b-instant",  # Groq model ID.
    "messages": [{"role": "user", "content": prompt}],  # User prompt.
}
req = urllib.request.Request(
    "https://api.groq.com/openai/v1/chat/completions",  # Groq chat endpoint.
    data=json.dumps(payload).encode("utf-8"),  # JSON-encode the payload.
    headers={
        "Authorization": f"Bearer {key}",  # Attach the API key.
        "Content-Type": "application/json",  # Send JSON.
        "User-Agent": "curl/8.0",  # Avoid Cloudflare 1010 blocks.
    },
)

try:
    with urllib.request.urlopen(req, timeout=10) as resp:  # Send the request.
        if resp.status == 200:
            data = json.loads(resp.read().decode("utf-8"))  # Parse JSON response.
            content = data["choices"][0]["message"]["content"]  # Extract reply text.
            print("success: Groq API key works")  # Success path.
            print(content)  # Print the model reply.
        else:
            print(resp.status)  # Non-200 status.
except urllib.error.HTTPError as exc:
    body = exc.read().decode("utf-8", errors="replace")  # Read error body.
    print(exc.code)  # Print HTTP error status code.
    if body:
        print(body)  # Print error details when available.
except Exception as exc:
    print(f"error: {exc}")  # Catch-all for unexpected errors.
