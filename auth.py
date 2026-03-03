import json
from datetime import datetime
import streamlit as st
from config import USERS_FILE, DATA_DIR, HISTORY_DIR


def _ensure_data_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def _load_users():
    _ensure_data_dirs()
    if USERS_FILE.exists():
        return json.loads(USERS_FILE.read_text())
    return {}


def _save_users(users):
    _ensure_data_dirs()
    USERS_FILE.write_text(json.dumps(users, indent=2))


def register_user(username, pin):
    if not username or not pin:
        return False, "Username and PIN are required."
    if len(pin) != 4 or not pin.isdigit():
        return False, "PIN must be exactly 4 digits."
    username = username.strip().lower()
    if not username:
        return False, "Username cannot be empty."
    users = _load_users()
    if username in users:
        return False, "Username already taken."
    users[username] = {
        "pin": pin,
        "created_at": datetime.now().isoformat(),
    }
    _save_users(users)
    return True, "Registration successful! You can now login."


def authenticate(username, pin):
    username = username.strip().lower()
    users = _load_users()
    user = users.get(username)
    if user and user["pin"] == pin:
        return True
    return False


def render_auth_page():
    st.markdown("### Login or Register")
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_user")
            pin = st.text_input("PIN (4 digits)", type="password", max_chars=4, key="login_pin")
            submitted = st.form_submit_button("Login", type="primary")
        if submitted:
            if authenticate(username, pin):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username.strip().lower()
                st.rerun()
            else:
                st.error("Invalid username or PIN.")

    with tab_register:
        with st.form("register_form"):
            new_user = st.text_input("Choose a Username", key="reg_user")
            new_pin = st.text_input("Choose a PIN (4 digits)", type="password", max_chars=4, key="reg_pin")
            submitted = st.form_submit_button("Register", type="primary")
        if submitted:
            success, msg = register_user(new_user, new_pin)
            if success:
                st.success(msg)
            else:
                st.error(msg)

    return st.session_state.get("authenticated", False)
