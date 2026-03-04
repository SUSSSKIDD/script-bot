from urllib.parse import quote_plus
from pymongo import MongoClient
from config import MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_APP, MONGO_DB_NAME

_client = None


def _build_uri():
    user = quote_plus(MONGO_USER)
    password = quote_plus(MONGO_PASS)
    return f"mongodb+srv://{user}:{password}@{MONGO_HOST}/?appName={MONGO_APP}"


def get_client():
    global _client
    if _client is None:
        _client = MongoClient(_build_uri())
    return _client


def get_db():
    client = get_client()
    return client[MONGO_DB_NAME]
