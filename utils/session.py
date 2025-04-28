from fastapi import Request, HTTPException

def get_logged_in_username(request: Request) -> str:
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Session expired or unauthorized")
    return username