from fastapi import APIRouter, Depends

from deps import get_current_user
from history_utils import load_history
from schemas import HistoryResponse, HistoryEntry

router = APIRouter(tags=["history"])


@router.get("/history", response_model=HistoryResponse)
def get_history(username: str = Depends(get_current_user)):
    entries = load_history(username)
    return {"entries": [
        HistoryEntry(
            id=e.get("id", ""),
            timestamp=e.get("timestamp", ""),
            inputs=e.get("inputs", {}),
            script=e.get("script", ""),
        )
        for e in entries
    ]}
