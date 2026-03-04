from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import GEMINI_API_KEY
from embeddings import sync_local_scripts
from routers import auth, scripts, generate, history


@asynccontextmanager
async def lifespan(app: FastAPI):
    if GEMINI_API_KEY:
        try:
            new = sync_local_scripts(GEMINI_API_KEY)
            if new > 0:
                print(f"Synced {new} local script(s) to MongoDB.")
        except Exception as e:
            print(f"Warning: failed to sync local scripts: {e}")
    yield


app = FastAPI(title="Script Bot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(scripts.router)
app.include_router(generate.router)
app.include_router(history.router)


@app.get("/")
@app.get("/health")
def health():
    return {"status": "ok"}
