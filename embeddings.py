import pickle
from datetime import datetime
from pathlib import Path

import faiss
import numpy as np
from PyPDF2 import PdfReader
from google import genai
from google.genai import types

from config import SCRIPTS_DIR, FAISS_DIR, EMBEDDING_MODEL, TOP_K_RESULTS


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(str(pdf_path))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


class EmbeddingStore:
    INDEX_FILE = FAISS_DIR / "index.faiss"
    META_FILE = FAISS_DIR / "metadata.pkl"

    def __init__(self):
        FAISS_DIR.mkdir(parents=True, exist_ok=True)
        self.metadata = {}  # {index_pos: {filename, text, embedded_at}}
        self.index = None
        self._load()

    def _load(self):
        if self.INDEX_FILE.exists() and self.META_FILE.exists():
            self.index = faiss.read_index(str(self.INDEX_FILE))
            with open(self.META_FILE, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            self.index = None
            self.metadata = {}

    def _save(self):
        if self.index is not None:
            faiss.write_index(self.index, str(self.INDEX_FILE))
        with open(self.META_FILE, "wb") as f:
            pickle.dump(self.metadata, f)

    def _embed_text(self, text, api_key, task_type="RETRIEVAL_DOCUMENT"):
        client = genai.Client(api_key=api_key)
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(task_type=task_type),
        )
        embedding = np.array(result.embeddings[0].values, dtype=np.float32)
        # Normalize for cosine similarity with IndexFlatIP
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding

    def _get_embedded_filenames(self):
        return {m["filename"] for m in self.metadata.values()}

    def sync_scripts(self, api_key):
        pdf_paths = sorted(SCRIPTS_DIR.glob("*.pdf"))
        already_embedded = self._get_embedded_filenames()
        new_pdfs = [p for p in pdf_paths if p.name not in already_embedded]

        for pdf_path in new_pdfs:
            text = extract_text_from_pdf(pdf_path)
            if not text:
                continue
            embedding = self._embed_text(text, api_key, task_type="RETRIEVAL_DOCUMENT")
            embedding_2d = embedding.reshape(1, -1)

            if self.index is None:
                dim = embedding.shape[0]
                self.index = faiss.IndexFlatIP(dim)

            idx = self.index.ntotal
            self.index.add(embedding_2d)
            self.metadata[idx] = {
                "filename": pdf_path.name,
                "text": text,
                "embedded_at": datetime.now().isoformat(),
            }

        if new_pdfs:
            self._save()

        total = self.index.ntotal if self.index else 0
        return total, len(new_pdfs)

    def query(self, query_text, api_key, top_k=None):
        if top_k is None:
            top_k = TOP_K_RESULTS
        if self.index is None or self.index.ntotal == 0:
            return []

        embedding = self._embed_text(query_text, api_key, task_type="RETRIEVAL_QUERY")
        embedding_2d = embedding.reshape(1, -1)

        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(embedding_2d, k)

        results = []
        for i in range(k):
            idx = int(indices[0][i])
            if idx >= 0 and idx in self.metadata:
                results.append(self.metadata[idx]["text"])
        return results
