import json
import re
from starlette.requests import Request

def remove_escape_characters(payload: bytes) -> str:
    """
    Decode bytes to str and remove common JSON escape sequences:
      - ‘\"’ → '"'
      - ‘\\/’ → '/'
      - ‘\\\\’ → '\\'
    """
    text = payload.decode('utf-8')
    text = re.sub(r'\\(["\\/])', r'\1', text)
    return text

async def parse_clean_json(request: Request) -> dict:
    """
    Reads raw body, cleans escapes, then loads JSON.
    """
    raw = await request.body()
    cleaned = remove_escape_characters(raw)
    return json.loads(cleaned)