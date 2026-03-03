import re
from urllib.parse import quote_plus

import streamlit as st
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB_NAME


def _fix_uri(uri):
    """URL-encode username and password in MongoDB URI to handle special characters."""
    match = re.match(r"^(mongodb(?:\+srv)?://)([^:]+):([^@]+)@(.+)$", uri)
    if match:
        scheme, user, password, rest = match.groups()
        return f"{scheme}{quote_plus(user)}:{quote_plus(password)}@{rest}"
    return uri


@st.cache_resource
def get_client():
    return MongoClient(_fix_uri(MONGO_URI))


def get_db():
    client = get_client()
    return client[MONGO_DB_NAME]
