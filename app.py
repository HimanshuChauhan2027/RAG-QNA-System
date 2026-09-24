"""DocQuery Streamlit entry point""".



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

    with tempfile.TemporaryDirectory(prefix="docquery_") as temporary_directory:
        save_uploaded_files(uploaded_files, temporary_directory)
        with st.spinner("Extracting text and creating chunks..."):
            documents = load_and_split_documents(temporary_directory)

        if not documents:
            st.error("No text could be extracted from the uploaded PDF files.")
            return

        with st.spinner("Generating embeddings and building the FAISS index..."):
            database = build_faiss_index(documents, INDEX_DIR, force_rebuild=True)

    st.session_state["retriever"] = database.as_retriever(search_kwargs={"k": TOP_K})
    st.session_state["processed_files"] = file_names
    st.session_state["messages"] = []
    st.success(f"Indexed {len(documents)} document chunks.")


def render_chat(prefer_groq: bool, groq_key, gemini_key) -> None:
    """Render chat history, query controls, and answer generation."""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for role, message in st.session_state["messages"]:
        render_message(role, message)

    def submit_query() -> None:
        question = st.session_state.get("query_input", "").strip()
        if question:
            st.session_state["messages"].append(("user", question))
            st.session_state["query_input"] = ""

    st.text_area("Ask a question about your documents", key="query_input")
    action_column, clear_column = st.columns(2)
    with action_column:
        st.button("Submit Question", on_click=submit_query, use_container_width=True)
    with clear_column:
        if st.button("Clear Conversation", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()

    messages = st.session_state["messages"]
    if not messages or messages[-1][0] != "user":
        return

    question = messages[-1][1]
    try:
        with st.spinner("Retrieving context and generating an answer..."):
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
    prefer_groq, rebuild = render_sidebar(groq_available, gemini_available)

    st.header("Upload PDFs")
    uploaded_files = st.file_uploader(
        "Upload one or more PDF files",
        accept_multiple_files=True,
        type=["pdf"],
        help="Upload PDF documents to create your searchable knowledge base.",
    )

    if not uploaded_files:
        render_empty_state()
        return

    process_uploads(uploaded_files, rebuild)
    if "retriever" not in st.session_state:
        return

    chat_tab, info_tab = st.tabs(["Chat", "About"])
    with chat_tab:
        st.markdown("### Chat with your documents")
        render_chat(prefer_groq, groq_key, gemini_key)
    with info_tab:
        render_info()

    st.markdown("---")
    st.caption("DocQuery | AI-Powered Document Q&A Chatbot")


if __name__ == "__main__":
    main()