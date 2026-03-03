import streamlit as st

from config import APP_TITLE, GEMINI_API_KEY, SCRIPTS_DIR
from auth import render_auth_page
from embeddings import EmbeddingStore
from generator import generate_script
from history import load_history, save_script, render_history_sidebar


def resolve_api_key():
    # Always show sidebar input so users can override with their own key
    with st.sidebar:
        user_key = st.text_input(
            "Your Gemini API Key (optional)",
            type="password",
            help="Paste your own key if the default one is exhausted. Get one at https://aistudio.google.com/apikey",
        )
    # User-provided key takes priority
    if user_key:
        return user_key
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

    # Sidebar: user info, logout, history
    with st.sidebar:
        st.markdown(f"Logged in as **{username}**")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
        st.divider()
        render_history_sidebar(username)

    # Check for reference scripts
    pdf_count = len(list(SCRIPTS_DIR.glob("*.pdf")))
    if pdf_count == 0:
        st.warning("No reference scripts found. Add PDF files to the `scripts/` folder.")
        return

    # Sync embeddings
    store = EmbeddingStore()
    if store.index is None or store.index.ntotal < pdf_count:
        with st.spinner(f"Embedding reference scripts ({pdf_count} PDFs)..."):
            total, new = store.sync_scripts(api_key)
        if new > 0:
            st.success(f"Embedded {new} new script(s). Total: {total}")

    # Main form
    render_generation_form(username, api_key)


if __name__ == "__main__":
    main()
