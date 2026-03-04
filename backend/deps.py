from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from config import SECRET_KEY, GEMINI_API_KEY

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("username")
        if not username:
            raise HTTPException(401, "Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")


def resolve_api_key(x_gemini_key: str | None = Header(None)) -> str:
    if x_gemini_key:
        return x_gemini_key
    if GEMINI_API_KEY:
        return GEMINI_API_KEY
    raise HTTPException(400, "No Gemini API key provided. Pass it via the X-Gemini-Key header.")
