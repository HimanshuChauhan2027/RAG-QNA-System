"""DocQuery Streamlit entry point"""



import tempfile

import streamlit as st
from dotenv import load_dotenv
from langchain_core.documents import Document

from config import INDEX_DIR, TOP_K
from documents import load_and_split_documents, save_uploaded_files
from llm import answer_question, provider_status
from logging_utils import log_event
from ui import (
    configure_page,
    render_empty_state,
    render_header,
    render_info,
    render_message,
    render_sidebar,
    render_styles,
)
from vector_store import build_faiss_index

load_dotenv()


def format_sources(source_documents: list[Document]) -> str:
    """Format retrieved documents with source filenames and one-based pages."""
    if not source_documents:
        return ""

    lines = ["**&#128218; Sources:**"]
    for index, document in enumerate(source_documents, start=1):
        source = document.metadata.get("source", f"Document {index}")
        page = document.metadata.get("page")
        page_reference = f", page {int(page) + 1}" if isinstance(page, int) else ""
        snippet = " ".join(document.page_content[:200].split())
        if len(document.page_content) > 200:
            snippet += "..."
        lines.extend([f"**[{index}]** {source}{page_reference}", f"> {snippet}"])
    return "\n".join(lines)


def process_uploads(uploaded_files, rebuild: bool) -> None:
    """Extract, chunk, embed, and index a new set of uploaded PDFs."""
    file_names = [uploaded_file.name for uploaded_file in uploaded_files]
    already_processed = st.session_state.get("processed_files") == file_names
    if already_processed and not rebuild:
        return

    st.session_state["document_status"] = "processing"
    st.session_state["document_status_files"] = file_names
    try:
        with tempfile.TemporaryDirectory(prefix="docquery_") as temporary_directory:
            save_uploaded_files(uploaded_files, temporary_directory)
            with st.spinner("Reading PDF pages and preparing searchable passages..."):
                documents = load_and_split_documents(temporary_directory)

            if not documents:
                st.session_state["document_status"] = "error"
                st.error("No text could be extracted from the selected PDF files.")
                return

            with st.spinner("Generating embeddings and building the FAISS index..."):
                database = build_faiss_index(documents, INDEX_DIR, force_rebuild=True)
    except Exception as error:
        st.session_state["document_status"] = "error"
        log_event(f"Document processing failed: {error}", "ERROR")
        st.error(f"Document processing failed: {error}")
        return

    st.session_state["retriever"] = database.as_retriever(search_kwargs={"k": TOP_K})
    st.session_state["processed_files"] = file_names
    st.session_state["document_status"] = "ready"
    st.session_state["messages"] = []
    st.success(f"Your documents are ready. Indexed {len(documents)} searchable passages.")


def queue_question(question: str) -> None:
    """Queue a suggested question for the chat input handler."""
    st.session_state["pending_question"] = question


def render_chat(prefer_groq: bool, groq_key, gemini_key) -> None:
    """Render chat history, query controls, and answer generation."""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for role, message in st.session_state["messages"]:
        render_message(role, message)

    if not st.session_state["messages"]:
        st.markdown("<div class='section-kicker'>TRY ASKING</div>", unsafe_allow_html=True)
        suggestions = [
            "Summarize the key ideas",
            "What are the main conclusions?",
            "Find important dates and figures",
        ]
        columns = st.columns(len(suggestions))
        for column, suggestion in zip(columns, suggestions):
            with column:
                st.button(
                    suggestion,
                    key=f"suggestion_{suggestion}",
                    use_container_width=True,
                    on_click=queue_question,
                    args=(suggestion,),
                )

    submitted_question = st.chat_input("Ask a question about your documents…")
    pending_question = st.session_state.pop("pending_question", "")
    question = (submitted_question or pending_question).strip()
    if not question:
        return

    st.session_state["messages"].append(("user", question))
    try:
        with st.spinner("Searching your documents and preparing an answer..."):
            answer, source_documents, model_name = answer_question(
                st.session_state["retriever"],
                question,
                prefer_groq,
                groq_key,
                gemini_key,
            )
        sources = format_sources(source_documents)
        response = answer
        if sources:
            response += f"\n\n{sources}"
        response += f"|||FOOTER:{model_name}"
        st.session_state["messages"].append(("assistant", response))
        log_event(f"Generated answer with {model_name}")
        st.rerun()
    except Exception as error:
        log_event(f"Question failed: {error}", "ERROR")
        st.error(str(error))


def main() -> None:
    configure_page()
    render_styles()
    render_header()

    groq_available, gemini_available, groq_key, gemini_key = provider_status()
    st.markdown("<div id='upload-pdf'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-kicker'>STEP 1 · ADD YOUR KNOWLEDGE BASE</div>", unsafe_allow_html=True)
    st.markdown("<h2 class='upload-title'>Upload your documents</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p class='hint-text'>Drop one or more PDF files here. DocQuery will extract, index, and prepare them for questions.</p>",
        unsafe_allow_html=True,
    )
    uploaded_files = st.file_uploader(
        "Drop PDF files here or browse",
        accept_multiple_files=True,
        type=["pdf"],
        help="Upload one or more PDF documents to create your searchable knowledge base.",
        key="document_uploader",
    )
    prefer_groq, rebuild = render_sidebar(
        groq_available,
        gemini_available,
        groq_key,
        gemini_key,
        uploaded_files,
    )

    if not uploaded_files:
        render_empty_state()
        return

    process_uploads(uploaded_files, rebuild)
    if (
        "retriever" not in st.session_state
        or st.session_state.get("processed_files") != [file.name for file in uploaded_files]
    ):
        return

    st.markdown("---")
    st.markdown("<div class='section-kicker'>STEP 2 · EXPLORE YOUR DOCUMENTS</div>", unsafe_allow_html=True)
    st.markdown("<h2>Ask DocQuery</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p class='hint-text'>Answers are generated from retrieved passages in your uploaded PDFs. Expand source passages to verify the context.</p>",
        unsafe_allow_html=True,
    )
    render_chat(prefer_groq, groq_key, gemini_key)

    st.markdown("---")
    render_info()


if __name__ == "__main__":
    main()