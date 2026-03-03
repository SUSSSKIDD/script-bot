import streamlit as st
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB_NAME


@st.cache_resource
def get_client():
    return MongoClient(MONGO_URI)


def get_db():
    client = get_client()
    return client[MONGO_DB_NAME]
