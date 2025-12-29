from dotenv import load_dotenv
import json
import os
import urllib.error
import urllib.request

SOURCE_PAGE_ID = "2c5813f2-6fb9-80a7-b85d-ffc672a811ab"
TARGET_PAGE_ID = "2d8813f2-6fb9-80de-9fd1-c649d4f0aeed"
NOTION_VERSION = "2022-06-28"


def load_api_key():
    key_before = os.getenv("NOTION_API_KEY")
    load_dotenv(override=False)
    key = os.getenv("NOTION_API_KEY")
    if not key:
        print("NOTION_API_KEY not set")
        raise SystemExit(1)
    if key_before:
        print("using NOTION_API_KEY from shell env")
    else:
        print("using NOTION_API_KEY from .env")
    return key


def make_headers(key):
    return {
        "Authorization": f"Bearer {key}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def request_json(url, headers, method="GET", payload=None):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode("utf-8")
        return resp.status, json.loads(body) if body else {}


def verify_key(headers):
    status, data = request_json("https://api.notion.com/v1/users/me", headers)
    if status == 200:
        name = data.get("name") or data.get("id")
        print("success: Notion API key works")
        if name:
            print(name)
    else:
        print(status)


def extract_rich_text(items):
    return "".join(item.get("plain_text", "") for item in items or [])


def read_page_text(page_id, headers):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    status, data = request_json(url, headers)
    if status != 200:
        print(status)
        return ""
    lines = []
    for block in data.get("results", []):
        block_type = block.get("type")
        content = block.get(block_type, {})
        text = extract_rich_text(content.get("rich_text"))
        if text:
            lines.append(text)
    return "\n".join(lines)


def append_paragraph(page_id, text, headers):
    if not text:
        print("no text to append")
        return
    payload = {
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": text}}]
                },
            }
        ]
    }
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    status, _ = request_json(url, headers, method="PATCH", payload=payload)
    if status == 200:
        print("appended to target page")
    else:
        print(status)


def get_input_prefix():
    return input("Prefix (optional): ").strip()


def main():
    key = load_api_key()
    headers = make_headers(key)
    try:
        verify_key(headers)
        text = read_page_text(SOURCE_PAGE_ID, headers)
        if text:
            print("source page text:")
            print(text)
        else:
            print("no text found on source page")
        prefix = get_input_prefix()
        if prefix and text:
            out_text = f"{prefix}\n{text}"
        else:
            out_text = prefix or text
        append_paragraph(TARGET_PAGE_ID, out_text, headers)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(exc.code)
        if body:
            print(body)
    except Exception as exc:
        print(f"error: {exc}")


if __name__ == "__main__":
    main()
