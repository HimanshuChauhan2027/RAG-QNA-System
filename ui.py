"""Streamlit presentation helpers."""

import datetime
import html

import streamlit as st

from config import CHUNK_SIZE, EMBEDDING_MODEL_NAME, TOP_K


def configure_page() -> None:
    st.set_page_config(
        page_title="DocQuery | Document Intelligence",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def render_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
            :root {
                --ink: #17233b;
                --muted: #69778d;
                --line: #e5eaf2;
                --accent: #3767e8;
                --accent-dark: #2854cc;
                --accent-soft: #edf3ff;
                --surface: #ffffff;
            }
            html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
            .stApp { background: #f5f7fb; color: var(--ink); }
            [data-testid='stHeader'] { background: transparent; }
            .main .block-container { max-width: 1240px; padding: 2rem 3.25rem 4rem; }
            h1, h2, h3 { font-family: 'Manrope', sans-serif !important; color: var(--ink) !important; letter-spacing: -.035em !important; }
            h1 { font-size: clamp(2rem, 4vw, 3.2rem) !important; line-height: 1.08 !important; font-weight: 800 !important; }
            h2 { font-size: 1.55rem !important; font-weight: 700 !important; }
            h3 { font-size: 1.08rem !important; font-weight: 700 !important; }
            p, li, label, [data-testid='stMarkdownContainer'] { color: var(--ink); }
            [data-testid='stSidebar'] { background: #111d33; border-right: 1px solid #25334b; }
            [data-testid='stSidebar'] * { color: #e7edf7; }
            [data-testid='stSidebar'] [data-testid='stMarkdownContainer'] p { color: #c4cfdf; }
            [data-testid='stSidebar'] hr { border-color: #2a3952; }
            [data-testid='stSidebar'] code { background: #24334d; color: #dce8ff; }
            [data-testid='stSidebar'] [data-testid='stExpander'] { border-color: #2a3952; }
            [data-testid='stSidebar'] .stButton > button {
                background: #24334d; color: #edf3ff; border: 1px solid #344661;
            }
            [data-testid='stSidebar'] .stButton > button:hover {
                background: #30425f; border-color: #506887; color: white;
            }
            .stButton > button, .stDownloadButton > button {
                min-height: 2.65rem; border-radius: 10px; font-weight: 700;
                transition: transform .15s ease, box-shadow .15s ease, background .15s ease;
            }
            .stButton > button[kind='primary'] {
                background: var(--accent); color: white; border: 1px solid var(--accent);
            }
            .stButton > button[kind='primary']:hover {
                background: var(--accent-dark); border-color: var(--accent-dark);
                transform: translateY(-1px); box-shadow: 0 8px 20px rgba(55,103,232,.2);
            }
            .stDownloadButton > button { border: 1px solid #344661; }
            [data-testid='stFileUploader'] {
                background: var(--surface); border: 1px solid var(--line);
                border-radius: 16px; padding: .55rem;
                box-shadow: 0 10px 30px rgba(26,42,69,.04);
            }
            [data-testid='stFileUploaderDropzone'] {
                background: #f8faff !important; border: 1px dashed #9bb6f5 !important;
                border-radius: 12px !important; min-height: 145px;
            }
            [data-testid='stFileUploaderDropzone'] [data-testid='stFileUploaderDropzoneInstructions'],
            [data-testid='stFileUploaderDropzone'] [data-testid='stFileUploaderDropzoneInstructions'] span {
                color: var(--ink) !important;
            }
            [data-testid='stFileUploaderDropzone'] [data-testid='stBaseButton-secondary'] {
                background: var(--accent) !important; color: white !important;
                border: 1px solid var(--accent) !important; border-radius: 8px !important;
                font-weight: 700;
            }
            [data-testid='stFileUploaderDropzone'] [data-testid='stBaseButton-secondary'] p { color: white !important; }
            [data-testid='stAlert'] { border-radius: 12px; }
            [data-testid='stChatMessage'] {
                background: var(--surface); border: 1px solid var(--line);
                border-radius: 16px; padding: .85rem 1rem; margin: .8rem 0;
                box-shadow: 0 8px 24px rgba(26,42,69,.035);
            }
            [data-testid='stChatMessage']:has([data-testid='chatAvatarIcon-user']) {
                background: #edf3ff; border-color: #dce7ff;
            }
            [data-testid='stChatInput'] textarea {
                background: white; border-color: #dce3ee; border-radius: 12px;
            }
            [data-testid='stChatInput'] textarea:focus {
                border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent);
            }
            [data-testid='stExpander'] { border-color: var(--line); border-radius: 10px; }
            .doc-header {
                background: linear-gradient(120deg, #ffffff 0%, #f0f5ff 100%);
                border: 1px solid var(--line); border-radius: 20px;
                padding: 1.8rem 2rem; margin: .2rem 0 2rem;
                box-shadow: 0 14px 36px rgba(26,42,69,.05);
            }
            .brand-row { display: flex; align-items: center; gap: .85rem; margin-bottom: .9rem; }
            .brand-mark {
                display: grid; place-items: center; width: 44px; height: 44px;
                color: white; border-radius: 13px;
                background: linear-gradient(145deg, #4c80f2, #2854cc);
                font-size: 1.35rem; box-shadow: 0 8px 18px rgba(55,103,232,.24);
            }
            .brand-name { font: 800 1.1rem 'Manrope', sans-serif; color: var(--ink); }
            .eyebrow { color: var(--accent); font-size: .72rem; font-weight: 700; letter-spacing: .13em; text-transform: uppercase; margin-bottom: .55rem; }
            .subtitle { color: var(--muted); font-size: 1rem; max-width: 670px; margin: .6rem 0 0; line-height: 1.65; }
            .section-kicker { color: var(--accent); font-size: .72rem; font-weight: 700; letter-spacing: .11em; text-transform: uppercase; margin: .2rem 0 .4rem; }
            .upload-title { margin: 0 0 .35rem !important; }
            .welcome-panel {
                background: white; border: 1px solid var(--line); border-radius: 16px;
                padding: 1.3rem 1.5rem; margin-top: 1.2rem;
                box-shadow: 0 10px 30px rgba(26,42,69,.04);
            }
            .welcome-panel strong { color: var(--ink); }
            .feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: .8rem; margin-top: 1rem; }
            .feature-card {
                background: white; border: 1px solid var(--line); border-radius: 14px;
                padding: 1rem; min-height: 105px;
            }
            .feature-card strong { display: block; margin: .4rem 0 .2rem; color: var(--ink); }
            .feature-card span { color: var(--muted); font-size: .86rem; line-height: 1.5; }
            .sidebar-brand { font: 800 1.3rem 'Manrope', sans-serif; color: white; margin: .4rem 0 1.7rem; }
            .sidebar-brand span { color: #8db0ff; }
            .sidebar-label { color: #8fa0b8; font-size: .68rem; font-weight: 700; letter-spacing: .13em; margin: 1.2rem 0 .55rem; }
            .sidebar-upload {
                display: block; padding: .75rem .85rem; border-radius: 10px;
                background: #263a5b; border: 1px solid #38537d; color: #fff !important;
                text-decoration: none !important; font-weight: 700; margin-bottom: .9rem;
            }
            .sidebar-upload:hover { background: #304873; }
            .sidebar-document {
                overflow-wrap: anywhere; background: #1b2b45; border: 1px solid #2e4261;
                border-radius: 9px; color: #d7e2f4; font-size: .82rem;
                padding: .55rem .65rem; margin: .35rem 0;
            }
            .sidebar-guide ol { margin: 0; padding-left: 1.35rem; }
            .sidebar-guide li { color: #c4cfdf; line-height: 1.55; padding-left: .2rem; margin: 0 0 .45rem; }
            .sidebar-guide li::marker { color: #8db0ff; font-weight: 700; }
            .status-pill { display: inline-block; border-radius: 99px; padding: .2rem .55rem; font-size: .74rem; font-weight: 700; }
            .status-ready { background: #173d38; color: #7de0be; }
            .status-waiting { background: #43391e; color: #f0cc71; }
            .status-error { background: #4a2a32; color: #ff9aa8; }
            .hint-text { color: var(--muted); font-size: .9rem; line-height: 1.6; }
            @media (max-width: 800px) {
                .main .block-container { padding: 1rem .85rem 2.5rem; }
                .doc-header { padding: 1.3rem 1.1rem; border-radius: 15px; }
                .feature-grid { grid-template-columns: 1fr; }
                [data-testid='stChatMessage'] { padding: .65rem .7rem; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class='doc-header'>
            <div class='brand-row'>
                <div class='brand-mark'>⌕</div>
                <div class='brand-name'>DocQuery</div>
            </div>
            <div class='eyebrow'>AI-POWERED DOCUMENT INTELLIGENCE</div>
            <h1>Answers are already in your documents.</h1>
            <p class='subtitle'>Bring your PDFs into focus. Ask natural-language questions and get grounded answers with relevant page references.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(
    groq_available: bool,
    gemini_available: bool,
    groq_key: str | None,
    gemini_key: str | None,
    uploaded_files=None,
) -> tuple[bool, bool]:
    """Render document status, navigation, model settings, and chat actions."""
    with st.sidebar:
        st.markdown("<div class='sidebar-brand'>Doc<span>Query</span></div>", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-label'>WORKSPACE</div>", unsafe_allow_html=True)
        st.markdown(
            "<a class='sidebar-upload' href='#upload-pdf'>＋ &nbsp; Upload PDF</a>",
            unsafe_allow_html=True,
        )

        uploaded_names = [file.name for file in uploaded_files] if uploaded_files else []
        indexed_names = st.session_state.get("processed_files", [])
        active_names = uploaded_names
        is_indexed = (
            "retriever" in st.session_state
            and bool(active_names)
            and active_names == indexed_names
        )
        failed_for_active_files = (
            st.session_state.get("document_status") == "error"
            and st.session_state.get("document_status_files") == active_names
        )
        status = (
            "Indexed"
            if is_indexed
            else "Needs attention"
            if failed_for_active_files
            else "Processing"
            if uploaded_names
            else "Waiting for PDF"
        )
        status_class = (
            "status-ready"
            if is_indexed
            else "status-error"
            if failed_for_active_files
            else "status-waiting"
        )

        st.markdown("<div class='sidebar-label'>CURRENT DOCUMENT</div>", unsafe_allow_html=True)
        if active_names:
            for name in active_names:
                st.markdown(
                    f"<div class='sidebar-document'>📄 &nbsp; {html.escape(name)}</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("<div class='sidebar-document'>No document selected</div>", unsafe_allow_html=True)
        st.markdown(
            f"<span class='status-pill {status_class}'>● &nbsp; {status}</span>",
            unsafe_allow_html=True,
        )

        st.markdown("<div class='sidebar-label'>CONVERSATION</div>", unsafe_allow_html=True)
        if st.button(
            "Clear conversation",
            use_container_width=True,
            disabled=not st.session_state.get("messages"),
        ):
            st.session_state["messages"] = []
            st.session_state.pop("pending_question", None)
            st.rerun()

        with st.expander("Settings & providers"):
            prefer_groq = st.checkbox(
                "Prefer Groq",
                value=groq_available and bool(groq_key),
            )
            st.caption(
                f"Groq · {'Ready' if groq_available and groq_key else 'Not configured'}"
            )
            st.caption(
                f"Gemini · {'Ready' if gemini_available and gemini_key else 'Not configured'}"
            )
            st.caption(
                f"Search uses {EMBEDDING_MODEL_NAME}, {CHUNK_SIZE}-character chunks, "
                f"and the top {TOP_K} matches."
            )
            rebuild = st.button(
                "Rebuild document index",
                use_container_width=True,
                disabled=not uploaded_names,
                help="Re-extract and re-index the currently selected PDFs.",
            )

        st.markdown("<div class='sidebar-label'>QUICK GUIDE</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='sidebar-guide'><ol>"
            "<li>Add PDF files from the upload area.</li>"
            "<li>Wait for indexing to finish.</li>"
            "<li>Ask a question in the chat.</li>"
            "</ol></div>",
            unsafe_allow_html=True,
        )

        if st.session_state.get("messages"):
            history = build_chat_history(st.session_state["messages"])
            st.download_button(
                "Download chat history",
                data=history,
                file_name=f"chat_history_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt",
                mime="text/plain",
                use_container_width=True,
            )
    return prefer_groq, rebuild


def build_chat_history(messages) -> str:
    lines = [f"Chat History - {datetime.datetime.now():%Y-%m-%d %H:%M:%S}", ""]
    for role, content in messages:
        clean_content = content.split("|||FOOTER:")[0].split("|||DEBUG_CHUNKS:")[0]
        lines.extend([f"[{role.upper()}]:", clean_content.strip(), "-" * 50, ""])
    return "\n".join(lines)


def render_info() -> None:
    st.markdown(
        """
        **How it works**
        DocQuery extracts PDF text page by page, splits it into searchable chunks, creates embeddings,
        and retrieves the most relevant passages from FAISS before generating an answer.

        **Language models:** Groq models are preferred when enabled; Gemini is available as a configured fallback.
        """
    )


def render_message(role: str, message: str) -> None:
    """Render one chat message and its source references."""
    if role == "user":
        with st.chat_message("user"):
            st.markdown(message)
        return

    answer_text, _, footer = message.partition("|||FOOTER:")
    answer_text, _, sources_text = answer_text.partition("**&#128218; Sources:**")
    with st.chat_message("assistant", avatar="📄"):
        st.markdown(answer_text.strip())
        if sources_text:
            with st.expander("View source passages"):
                st.markdown(sources_text)
        if footer:
            st.caption(f"Generated with {footer.strip()}")


def render_empty_state() -> None:
    st.markdown(
        """
        <div class='welcome-panel'>
            <div class='section-kicker'>YOUR DOCUMENT WORKSPACE</div>
            <strong>Start with a PDF. Leave with clarity.</strong><br>
            <span class='hint-text'>Upload one or more documents to create a searchable knowledge base for this session. Your answers will be grounded in the content and include source pages when available.</span>
            <div class='feature-grid'>
                <div class='feature-card'><span>01 · PREPARE</span><strong>Extract &amp; index</strong><span>PDF pages become searchable passages using the existing document pipeline.</span></div>
                <div class='feature-card'><span>02 · EXPLORE</span><strong>Ask naturally</strong><span>Use plain language to find details, compare ideas, or summarize sections.</span></div>
                <div class='feature-card'><span>03 · VERIFY</span><strong>Follow the sources</strong><span>Review retrieved snippets and page references alongside each answer.</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )