"""PDF upload, extraction, and chunking."""

import os
from pathlib import Path
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredPDFLoader
from langchain_core.documents import Document

from config import CHUNK_OVERLAP, CHUNK_SIZE
from logging_utils import log_event


def save_uploaded_files(uploaded_files, destination: str) -> list[str]:
    """Persist Streamlit uploads in a temporary directory for the loaders."""
    os.makedirs(destination, exist_ok=True)
    saved_paths = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(destination, uploaded_file.name)
        with open(file_path, "wb") as file_handle:
            file_handle.write(uploaded_file.getbuffer())
        saved_paths.append(file_path)
    return saved_paths


def load_and_split_documents(directory: str) -> List[Document]:
    """Extract PDF pages and split them into retrieval-sized documents."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
        length_function=len,
    )
    documents = []

    for pdf_path in Path(directory).glob("*.pdf"):
        try:
            pages = PyMuPDFLoader(str(pdf_path)).load()
            total_text = "".join(page.page_content for page in pages)

            if len(total_text.strip()) < 100:
                log_event(f"Low text content detected in {pdf_path.name}; trying fallback extraction.")
                try:
                    pages = UnstructuredPDFLoader(
                        str(pdf_path), mode="elements", strategy="hi_res"
                    ).load()
                except Exception as error:
                    log_event(f"Fallback extraction failed for {pdf_path.name}: {error}", "WARNING")

            chunks = splitter.split_documents(pages)
            documents.extend(
                Document(
                    page_content=chunk.page_content,
                    metadata={**chunk.metadata, "source": pdf_path.name},
                )
                for chunk in chunks
            )
            log_event(f"Created {len(chunks)} chunks from {pdf_path.name}")
        except Exception as error:
            log_event(f"Error loading {pdf_path.name}: {error}", "ERROR")

    return documents