import json
import uuid
from datetime import datetime

import streamlit as st

from config import HISTORY_DIR


def _get_history_path(username):
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    return HISTORY_DIR / f"{username}.json"


def load_history(username):
    path = _get_history_path(username)
    if path.exists():
        return json.loads(path.read_text())
    return []


def save_script(username, user_inputs, generated_script):
    history = load_history(username)
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "inputs": user_inputs,
        "script": generated_script,
    }
    history.append(entry)
    path = _get_history_path(username)
    path.write_text(json.dumps(history, indent=2))


def render_history_sidebar(username):
    history = load_history(username)
    st.markdown(f"**Generated Scripts: {len(history)}**")

    if not history:
        st.caption("No scripts generated yet.")
        return

    for entry in reversed(history):
        ts = entry["timestamp"][:16].replace("T", " ")
        topic = entry["inputs"].get("topic", "Untitled")
        label = f"{ts} — {topic[:30]}"
        with st.expander(label):
            st.markdown(entry["script"])
