"""Streamlit presentation helpers."""

import datetime
import html
import os

import streamlit as st

from config import CHUNK_SIZE, EMBEDDING_MODEL_NAME, TOP_K


def configure_page() -> None:
    st.set_page_config(
        page_title="DocQuery | AI-Powered Document Q&A Chatbot",
        page_icon=":books:",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def render_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
            :root { --ink: #20243a; --muted: #697087; --line: #e6e8f0; --accent: #5654d9; --accent-soft: #eeedff; --paper: #fbfbfd; }
            * { font-family: 'DM Sans', sans-serif; }
            .stApp { background: #f2f3f8; }
            .main .block-container { max-width: 1180px; padding: 2.5rem 3.5rem 4rem; }
            [data-testid='stHeader'] { background: transparent; }
            h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; color: var(--ink) !important; letter-spacing: 0 !important; }
            h1 { font-size: clamp(2.3rem, 5vw, 4.2rem) !important; line-height: 1 !important; font-weight: 700 !important; }
            h2 { font-size: 1.6rem !important; margin-top: 1.5rem !important; }
            h3 { font-size: 1.15rem !important; }
            p, li, label, [data-testid='stMarkdownContainer'] { color: var(--ink); }
            [data-testid='stSidebar'] { background: #20243a; border-right: 0; }
            [data-testid='stSidebar'] * { color: #eef0ff !important; }
            [data-testid='stSidebar'] hr { border-color: rgba(255,255,255,.14); }
            [data-testid='stSidebar'] code { background: rgba(255,255,255,.1); color: #d9d8ff !important; }
            [data-testid='stSidebar'] .stButton > button { background: #6866e5; border: 1px solid #8583f2; }
            .stButton > button { min-height: 2.7rem; background: var(--accent); color: white; border: 0; border-radius: 8px; font-weight: 700; transition: transform .15s ease, box-shadow .15s ease; }
            .stButton > button:hover { background: #4543bb; color: white; transform: translateY(-1px); box-shadow: 0 8px 18px rgba(86,84,217,.2); }
            .stDownloadButton > button { border-radius: 8px; font-weight: 600; }
            .stTextArea textarea { background: white !important; color: var(--ink) !important; border: 1px solid #dfe1eb !important; border-radius: 10px !important; padding: .9rem !important; }
            .stTextArea textarea:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 1px var(--accent) !important; }
            [data-testid='stFileUploader'] { background: white; border: 1px dashed #b9b9dc; border-radius: 12px; padding: .4rem; }
            [data-testid='stAlert'] { border-radius: 10px; }
            .doc-header { padding: .5rem 0 2.5rem; }
            .eyebrow { color: var(--accent); font-size: .75rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; margin-bottom: .7rem; }
            .subtitle { color: var(--muted); font-size: 1.05rem; max-width: 600px; margin-top: .7rem; }
            .welcome-panel { background: white; border: 1px solid var(--line); border-radius: 14px; padding: 1.35rem 1.5rem; box-shadow: 0 10px 30px rgba(32,36,58,.05); }
            .welcome-panel strong { color: var(--ink); }
            .chat-user, .chat-assistant { border-radius: 12px; padding: 1rem 1.15rem; margin: .7rem 0; line-height: 1.65; }
            .chat-user { background: var(--accent-soft); border: 1px solid #dcdaff; margin-left: 12%; }
            .chat-assistant { background: white; border: 1px solid var(--line); box-shadow: 0 5px 18px rgba(32,36,58,.04); margin-right: 8%; }
            .chat-label { color: var(--accent); font-size: .76rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; margin-bottom: .35rem; }
            .sidebar-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.4rem; font-weight: 700; margin-bottom: 1.5rem; }
            @media (max-width: 800px) { .main .block-container { padding: 1.5rem 1rem 3rem; } .chat-user, .chat-assistant { margin-left: 0; margin-right: 0; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class='doc-header'>
            <div class='eyebrow'>DOCUMENT Q&amp;A, MADE SIMPLE</div>
            <h1>DocQuery</h1>
            <p class='subtitle'>Upload your PDFs, ask anything, and find clear answers with the relevant sources.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(groq_available: bool, gemini_available: bool) -> tuple[bool, bool]:
    """Render settings and return the user's provider and rebuild choices."""
    with st.sidebar:
        st.markdown("<div class='sidebar-title'>DocQuery settings</div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            **Search configuration**

            - Embeddings: `{EMBEDDING_MODEL_NAME}`
            - Chunk size: `{CHUNK_SIZE}`
            - Results per query: `{TOP_K}`
            """
        )

        groq_key = bool(os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY"))
        gemini_key = bool(os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY"))
        prefer_groq = st.checkbox("Prefer Groq", value=groq_available and groq_key)
        rebuild = st.button("Rebuild Index", help="Rebuild the FAISS index from the current upload")

        st.markdown("**Model providers**")
        groq_status = "Ready" if groq_available and groq_key else "Not configured"
        gemini_status = "Ready" if gemini_available and gemini_key else "Not configured"
        st.markdown(f"`{'OK' if groq_status == 'Ready' else '--'}` Groq  |  {groq_status}")
        st.markdown(f"`{'OK' if gemini_status == 'Ready' else '--'}` Gemini  |  {gemini_status}")

        if st.session_state.get("messages"):
            history = build_chat_history(st.session_state["messages"])
            st.download_button(
                "Download Chat History",
                data=history,
                file_name=f"chat_history_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt",
                mime="text/plain",
            )
    return prefer_groq, rebuild


def build_chat_history(messages) -> str:
    lines = [f"Chat History - {datetime.datetime.now():%Y-%m-%d %H:%M:%S}", ""]
    for role, content in messages:
        clean_content = content.split("|||FOOTER:")[0].split("|||DEBUG_CHUNKS:")[0]
        lines.extend([f"[{role.upper()}]:", clean_content.strip(), "-" * 50, ""])
    return "\n".join(lines)


def render_info() -> None:
    st.markdown("### About DocQuery")
    st.markdown(
        """
        Upload PDF documents, let DocQuery build a searchable vector index, and ask questions about the uploaded content.

        **Workflow:** PDF upload -> text extraction -> chunking -> embeddings -> FAISS retrieval -> generated answer with sources.

        **Supported providers:** Groq models, with Gemini available as a fallback when configured.
        """
    )


def render_message(role: str, message: str) -> None:
    """Render one chat message and its source references."""
    if role == "user":
        st.markdown(
            f"<div class='chat-user'><div class='chat-label'>You</div>{html.escape(message)}</div>",
            unsafe_allow_html=True,
        )
        return

    answer_text, _, footer = message.partition("|||FOOTER:")
    answer_text, _, sources_text = answer_text.partition("**&#128218; Sources:**")
    st.markdown(
        f"<div class='chat-assistant'><div class='chat-label'>DocQuery</div>{html.escape(answer_text.strip()).replace(chr(10), '<br>')}</div>",
        unsafe_allow_html=True,
    )

    if sources_text:
        with st.expander("View Sources", expanded=False):
            for line in sources_text.splitlines():
                if line.strip():
                    st.markdown(line)
    if footer:
        st.caption(f"Generated with: {footer.strip()}")


def render_empty_state() -> None:
    st.markdown(
        """
        <div class='welcome-panel'>
            <strong>Start with your documents</strong><br>
            <span>Upload one or more PDFs above. DocQuery will extract the text, build a searchable index, and keep the conversation grounded in your files.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )