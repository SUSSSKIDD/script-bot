import uuid
from datetime import datetime

import streamlit as st
from db import get_db


def load_history(username):
    db = get_db()
    entries = list(db.history.find({"username": username}).sort("timestamp", -1))
    return entries


def save_script(username, user_inputs, generated_script):
    db = get_db()
    db.history.insert_one({
        "username": username,
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "inputs": user_inputs,
        "script": generated_script,
    })


def render_history_sidebar(username):
    history = load_history(username)
    st.markdown(f"**Generated Scripts: {len(history)}**")

    if not history:
        st.caption("No scripts generated yet.")
        return

    for entry in history:
        ts = entry["timestamp"][:16].replace("T", " ")
        topic = entry["inputs"].get("topic", "Untitled")
        label = f"{ts} — {topic[:30]}"
        with st.expander(label):
            st.markdown(entry["script"])
