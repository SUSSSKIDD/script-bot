from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from db import get_db
from deps import get_current_user, resolve_api_key
from embeddings import upload_script, delete_script, get_script_count
from schemas import ScriptsListResponse, ScriptEntry, MessageResponse

router = APIRouter(prefix="/scripts", tags=["scripts"])


@router.get("", response_model=ScriptsListResponse)
def list_scripts(username: str = Depends(get_current_user)):
    db = get_db()
    docs = list(db.scripts.find({}, {"filename": 1, "uploaded_at": 1}))
    scripts = [
        ScriptEntry(filename=d["filename"], uploaded_at=d.get("uploaded_at", ""))
        for d in docs
    ]
    return {"count": len(scripts), "scripts": scripts}


@router.post("/upload", response_model=MessageResponse, status_code=201)
def upload(
    file: UploadFile = File(...),
    username: str = Depends(get_current_user),
    api_key: str = Depends(resolve_api_key),
):
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are allowed.")

    pdf_bytes = file.file.read()
    success, msg = upload_script(file.filename, pdf_bytes, api_key)
    if not success:
        raise HTTPException(400, msg)
    return {"message": msg}


@router.delete("/{filename}", response_model=MessageResponse)
def remove(filename: str, username: str = Depends(get_current_user)):
    deleted = delete_script(filename)
    if not deleted:
        raise HTTPException(404, "Script not found.")
    return {"message": f"'{filename}' deleted."}
