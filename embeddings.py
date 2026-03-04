import io
from datetime import datetime
from pathlib import Path

import numpy as np
from PyPDF2 import PdfReader
from google import genai
from google.genai import types

from config import SCRIPTS_DIR, EMBEDDING_MODEL, TOP_K_RESULTS
from db import get_db


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(str(pdf_path))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def extract_text_from_bytes(pdf_bytes):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def _embed_text(text, api_key, task_type="RETRIEVAL_DOCUMENT"):
    client = genai.Client(api_key=api_key)
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(task_type=task_type),
    )
    embedding = np.array(result.embeddings[0].values, dtype=np.float32)
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    return embedding


def upload_script(filename, pdf_bytes, api_key):
    """Extract text from PDF, embed it, and store text + embedding in MongoDB."""
    db = get_db()
    text = extract_text_from_bytes(pdf_bytes)
    if not text:
        return False, "Could not extract text from PDF."

    if db.scripts.find_one({"filename": filename}):
        return False, f"'{filename}' already exists."

    embedding = _embed_text(text, api_key, task_type="RETRIEVAL_DOCUMENT")

    db.scripts.insert_one({
        "filename": filename,
        "text": text,
        "embedding": embedding.tolist(),
        "uploaded_at": datetime.now().isoformat(),
    })
    return True, f"'{filename}' uploaded successfully."


def sync_local_scripts(api_key):
    """Embed any local PDFs from scripts/ folder that aren't in MongoDB yet."""
    db = get_db()
    existing = {doc["filename"] for doc in db.scripts.find({}, {"filename": 1})}
    new_count = 0

    for pdf_path in sorted(SCRIPTS_DIR.glob("*.pdf")):
        if pdf_path.name in existing:
            continue
        text = extract_text_from_pdf(pdf_path)
        if not text:
            continue
        embedding = _embed_text(text, api_key, task_type="RETRIEVAL_DOCUMENT")
        db.scripts.insert_one({
            "filename": pdf_path.name,
            "text": text,
            "embedding": embedding.tolist(),
            "uploaded_at": datetime.now().isoformat(),
        })
        new_count += 1

    return new_count


def get_script_count():
    """Get total number of scripts in MongoDB."""
    db = get_db()
    return db.scripts.count_documents({})


def delete_script(filename):
    """Delete a script from MongoDB."""
    db = get_db()
    result = db.scripts.delete_one({"filename": filename})
    return result.deleted_count > 0


def query_similar_scripts(query_text, api_key, top_k=None):
    """Embed query and find top-K most similar scripts from MongoDB."""
    if top_k is None:
        top_k = TOP_K_RESULTS

    db = get_db()
    all_scripts = list(db.scripts.find({}, {"text": 1, "embedding": 1}))
    if not all_scripts:
        return []

    query_embedding = _embed_text(query_text, api_key, task_type="RETRIEVAL_QUERY")

    # Compute cosine similarity with each script
    scored = []
    for doc in all_scripts:
        if not doc.get("embedding"):
            continue
        doc_embedding = np.array(doc["embedding"], dtype=np.float32)
        score = float(np.dot(query_embedding, doc_embedding))
        scored.append((score, doc["text"]))

    # Sort by similarity (highest first) and return top-K texts
    scored.sort(key=lambda x: x[0], reverse=True)
    return [text for _, text in scored[:top_k]]
