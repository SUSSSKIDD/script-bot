import streamlit as st

from config import APP_TITLE, GEMINI_API_KEY, SCRIPTS_DIR
from auth import render_auth_page
from embeddings import upload_script, sync_local_scripts, get_script_count, delete_script
from generator import generate_script
from history import save_script, render_history_sidebar
from db import get_db


def resolve_api_key():
    # Always show sidebar input so users can override with their own key
    with st.sidebar:
        user_key = st.text_input(
            "Your Gemini API Key (optional)",
            type="password",
            help="Paste your own key if the default one is exhausted. Get one at https://aistudio.google.com/apikey",
            key="user_api_key",
        )
    # User-provided key ALWAYS takes priority over default
    if user_key and user_key.strip():
        return user_key.strip()
    # Then .env
    if GEMINI_API_KEY:
        return GEMINI_API_KEY
    # Then Streamlit secrets
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return None


def render_upload_section(api_key):
    """Render the PDF upload and manage scripts section in sidebar."""
    with st.sidebar:
        st.divider()
        st.markdown("**Reference Scripts**")

        # Show current script count
        count = get_script_count()
        st.caption(f"{count} script(s) loaded")

        # Upload new PDFs
        uploaded_files = st.file_uploader(
            "Upload PDF scripts",
            type=["pdf"],
            accept_multiple_files=True,
            key="pdf_uploader",
        )
        if uploaded_files and not st.session_state.get("upload_done", False):
            any_new = False
            for f in uploaded_files:
                with st.spinner(f"Processing {f.name}..."):
                    success, msg = upload_script(f.name, f.read(), api_key)
                if success:
                    st.success(msg)
                    any_new = True
            if any_new:
                st.session_state["upload_done"] = True
                st.rerun()
        if not uploaded_files:
            st.session_state["upload_done"] = False

        # List uploaded scripts with delete option
        db = get_db()
        uploaded_docs = list(db.scripts.find({}, {"filename": 1}))
        if uploaded_docs:
            with st.expander(f"Manage scripts ({len(uploaded_docs)})"):
                for doc in uploaded_docs:
                    col1, col2 = st.columns([3, 1])
                    col1.caption(doc["filename"])
                    if col2.button("X", key=f"del_{doc['filename']}"):
                        delete_script(doc["filename"])
                        st.rerun()


def render_generation_form(username, api_key):
    with st.form("script_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Person's Name *", placeholder="Tejaswini Johri")
            college = st.text_input("Masters College *", placeholder="Imperial College London")
            field = st.text_input("Field of Study *", placeholder="Economics & Strategy for Business")
        with col2:
            situation = st.text_input("Current Situation *", placeholder="now living and working in London")
            topic = st.text_input("Topic / Title *", placeholder="UK Masters Roadmap 2026")

        submitted = st.form_submit_button("Generate Script", type="primary", use_container_width=True)

    if submitted:
        user_inputs = {
            "name": name.strip(),
            "college": college.strip(),
            "field": field.strip(),
            "situation": situation.strip(),
            "topic": topic.strip(),
        }
        if not all(user_inputs.values()):
            st.error("All fields are required.")
            return

        with st.spinner("Generating your script..."):
            script = generate_script(user_inputs, api_key)

        st.session_state["last_script"] = script
        st.session_state["last_inputs"] = user_inputs
        save_script(username, user_inputs, script)

    # Display last generated script
    if "last_script" in st.session_state:
        st.divider()
        st.subheader("Generated Script")
        st.markdown(st.session_state["last_script"])

        st.divider()
        st.caption("Copy-friendly version:")
        st.code(st.session_state["last_script"], language=None)

        if st.button("Regenerate", use_container_width=True):
            with st.spinner("Regenerating..."):
                script = generate_script(st.session_state["last_inputs"], api_key)
            st.session_state["last_script"] = script
            save_script(username, st.session_state["last_inputs"], script)
            st.rerun()


def main():
    st.set_page_config(page_title=APP_TITLE, layout="centered")
    st.title(APP_TITLE)

    # Auth gate
    if not st.session_state.get("authenticated", False):
        render_auth_page()
        return

    username = st.session_state["username"]

    # API key
    api_key = resolve_api_key()
    if not api_key:
        st.warning("Please enter your Gemini API key in the sidebar to continue.")
        return

    # Sidebar: user info, logout
    with st.sidebar:
        st.markdown(f"Logged in as **{username}**")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    # Sync any local scripts from scripts/ folder into MongoDB
    if not st.session_state.get("local_synced", False):
        new = sync_local_scripts(api_key)
        if new > 0:
            st.success(f"Synced {new} local script(s).")
        st.session_state["local_synced"] = True

    # Upload section in sidebar
    render_upload_section(api_key)

    # Sidebar history
    with st.sidebar:
        st.divider()
        render_history_sidebar(username)

    # Check for reference scripts
    if get_script_count() == 0:
        st.warning("No reference scripts found. Upload PDF scripts using the sidebar.")
        return

    # Main form
    render_generation_form(username, api_key)


if __name__ == "__main__":
    main()
