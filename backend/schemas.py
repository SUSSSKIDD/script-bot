from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    username: str
    pin: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")


class AuthResponse(BaseModel):
    token: str
    username: str


class MessageResponse(BaseModel):
    message: str


class GenerateRequest(BaseModel):
    name: str
    college: str
    field: str
    situation: str
    topic: str


class GenerateResponse(BaseModel):
    script: str


class ScriptEntry(BaseModel):
    filename: str
    uploaded_at: str


class ScriptsListResponse(BaseModel):
    count: int
    scripts: list[ScriptEntry]


class HistoryEntry(BaseModel):
    id: str
    timestamp: str
    inputs: dict
    script: str


class HistoryResponse(BaseModel):
    entries: list[HistoryEntry]
