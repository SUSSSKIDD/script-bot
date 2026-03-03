from urllib.parse import quote_plus

import streamlit as st
from pymongo import MongoClient
from config import MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_APP, MONGO_DB_NAME


def _build_uri():
    user = quote_plus(MONGO_USER)
    password = quote_plus(MONGO_PASS)
    return f"mongodb+srv://{user}:{password}@{MONGO_HOST}/?appName={MONGO_APP}"


@st.cache_resource
def get_client():
    return MongoClient(_build_uri())


def get_db():
    client = get_client()
    return client[MONGO_DB_NAME]
