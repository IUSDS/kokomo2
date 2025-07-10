import json
import re
from starlette.requests import Request
from fastapi import HTTPException

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
    raw = await request.body()
    text = raw.decode('utf-8')

    # Common JSON fixes:
    text = re.sub(r"'", '"', text)  # single → double quotes
    text = re.sub(r",\s*([}\]])", r"\1", text)  # remove trailing commas before } or ]

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON decode error: {str(e)}")