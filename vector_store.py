"""Embedding and FAISS index construction."""

import os
import shutil

import streamlit as st
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from config import EMBEDDING_MODEL_NAME
from logging_utils import log_event


@st.cache_resource
def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)


def build_faiss_index(
    documents: list[Document], index_directory: str, force_rebuild: bool = True
) -> FAISS:
    """Build the index for the current upload, optionally reusing a valid local index."""
    embeddings = get_embeddings()

    if os.path.exists(index_directory) and not force_rebuild:
        try:
            return FAISS.load_local(
                index_directory,
                embeddings,
                allow_dangerous_deserialization=True,
            )
        except Exception as error:
            log_event(f"Existing FAISS index could not be loaded: {error}", "WARNING")
            shutil.rmtree(index_directory, ignore_errors=True)

    database = FAISS.from_documents(documents, embeddings)
    os.makedirs(index_directory, exist_ok=True)
    database.save_local(index_directory)
    log_event(f"Built FAISS index from {len(documents)} chunks")
    return database