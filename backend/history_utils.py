import uuid
from datetime import datetime

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
