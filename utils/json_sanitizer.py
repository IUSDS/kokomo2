import json
import re
from starlette.requests import Request
from fastapi import HTTPException

def remove_escape_characters(payload: bytes) -> str:
    """
    Decode bytes to str and remove common JSON escape sequences:
      - '\"' → '"'
      - '\\/' → '/'
      - '\\\\' → '\\'
    """
    text = payload.decode('utf-8')
    text = re.sub(r'\\(["\\/])', r'\1', text)
    return text

async def parse_clean_json(request: Request) -> dict:
    raw = await request.body()
    text = raw.decode('utf-8')
    
    # First, try parsing as-is
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Apply fixes only if initial parsing failed
    original_text = text
    
    # Fix 1: Remove escape characters
    text = remove_escape_characters(raw)
    
    # Fix 2: More careful quote replacement - only replace quotes that are clearly property names
    # This regex looks for single quotes around keys (not inside string values)
    text = re.sub(r"(\s*)('([^']*)')\s*:", r'\1"\3":', text)
    
    # Fix 3: Remove trailing commas before } or ] more carefully
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    
    # Fix 4: Handle unquoted keys (common in JavaScript-like JSON)
    text = re.sub(r'(\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:', r'\1"\2":', text)
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Log the problematic text for debugging
        error_line = original_text.split('\n')[e.lineno - 1] if e.lineno <= len(original_text.split('\n')) else "Line not found"
        raise HTTPException(
            status_code=400, 
            detail=f"JSON decode error: {str(e)}\nProblematic line: {error_line[:100]}..."
        )

# Alternative: More conservative approach
# async def parse_clean_json_conservative(request: Request) -> dict:
#     raw = await request.body()
#     text = raw.decode('utf-8')
    
#     try:
#         return json.loads(text)
#     except json.JSONDecodeError as e:
#         # Only apply minimal fixes
#         text = re.sub(r",(\s*[}\]])", r"\1", text)  # Remove trailing commas
        
#         try:
#             return json.loads(text)
#         except json.JSONDecodeError as e2:
#             # Provide more detailed error information
#             lines = text.split('\n')
#             error_line = lines[e2.lineno - 1] if e2.lineno <= len(lines) else "Line not found"
            
#             raise HTTPException(
#                 status_code=400,
#                 detail={
#                     "error": "JSON decode error",
#                     "message": str(e2),
#                     "line": e2.lineno,
#                     "column": e2.colno,
#                     "problematic_text": error_line[max(0, e2.colno-20):e2.colno+20]
#                 }
#             )