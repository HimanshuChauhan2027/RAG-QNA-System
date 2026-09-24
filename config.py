"""Application configuration and model settings."""

import os

INDEX_DIR = "faiss_index_storage"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K = 10

def _configured_models(variable_name: str, defaults: list[str]) -> list[str]:
    """Return comma-separated model overrides, or the current defaults."""
    configured = os.getenv(variable_name, "")
    models = [model.strip() for model in configured.split(",") if model.strip()]
    return models or defaults


GROQ_MODELS = _configured_models(
    "GROQ_MODELS",
    [
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "allam-2-7b",
    ],
)

GEMINI_MODELS = _configured_models("GEMINI_MODELS", ["gemini-3.6-flash"])

QUESTION_PROMPT = """
You are an expert AI assistant helping users understand their documents.

Context from the uploaded documents:
{context}

Question: {input}

Instructions:
- Review the context for information relevant to the question.
- Answer using the context whenever possible.
- If the context does not contain the answer, say that the information was not found in the uploaded documents.
- Be clear, accurate, and concise.

Answer:
"""