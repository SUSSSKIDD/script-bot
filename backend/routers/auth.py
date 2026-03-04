from datetime import datetime

import jwt
from fastapi import APIRouter, HTTPException

from config import SECRET_KEY
from db import get_db
from schemas import AuthRequest, AuthResponse, MessageResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=MessageResponse, status_code=201)
def register(data: AuthRequest):
    username = data.username.strip().lower()
    if not username:
        raise HTTPException(400, "Username cannot be empty.")

    db = get_db()
    if db.users.find_one({"username": username}):
        raise HTTPException(400, "Username already taken.")

    db.users.insert_one({
        "username": username,
        "pin": data.pin,
        "created_at": datetime.now().isoformat(),
    })
    return {"message": "Registration successful."}


@router.post("/login", response_model=AuthResponse)
def login(data: AuthRequest):
    username = data.username.strip().lower()
    db = get_db()
    user = db.users.find_one({"username": username, "pin": data.pin})
    if not user:
        raise HTTPException(401, "Invalid username or PIN.")

    token = jwt.encode({"username": username}, SECRET_KEY, algorithm="HS256")
    return {"token": token, "username": username}
