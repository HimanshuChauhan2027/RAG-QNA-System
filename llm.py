"""LLM selection and retrieval-augmented answer generation."""

import os
from typing import Optional

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from config import GEMINI_MODELS, GROQ_MODELS, QUESTION_PROMPT

try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None


def provider_status() -> tuple[bool, bool, Optional[str], Optional[str]]:
    """Return provider availability and configured keys."""
    import streamlit as st

    groq_key = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    return ChatGroq is not None, ChatGoogleGenerativeAI is not None, groq_key, gemini_key


def answer_question(retriever, question: str, prefer_groq: bool, groq_key, gemini_key):
    """Try configured providers and return the answer plus retrieved source documents."""
    available_models = []
    if prefer_groq and ChatGroq is not None and groq_key:
        available_models.extend((model, "groq") for model in GROQ_MODELS)
    if ChatGoogleGenerativeAI is not None and gemini_key:
        available_models.extend((model, "gemini") for model in GEMINI_MODELS)

    if not available_models:
        raise RuntimeError("No LLM configured. Set GROQ_API_KEY or GEMINI_API_KEY.")

    prompt = ChatPromptTemplate.from_template(QUESTION_PROMPT)
    errors = []
    for model_name, provider in available_models:
        try:
            if provider == "groq":
                model = ChatGroq(
                    groq_api_key=groq_key,
                    model_name=model_name,
                    temperature=0.0,
                    max_tokens=4096,
                )
            else:
                model = ChatGoogleGenerativeAI(
                    google_api_key=gemini_key,
                    model=model_name,
                    temperature=0.0,
                    max_output_tokens=4096,
                )

            document_chain = create_stuff_documents_chain(model, prompt)
            retrieval_chain = create_retrieval_chain(retriever, document_chain)
            result = retrieval_chain.invoke({"input": question})
            return result.get("answer", "No answer generated"), result.get("context", []), model_name
        except Exception as error:
            errors.append(f"{model_name}: {error}")

    raise RuntimeError("All configured models failed. " + " | ".join(errors))