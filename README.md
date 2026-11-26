# DocQuery

## AI-Powered Document Q&A Chatbot

## Overview

DocQuery is a Streamlit application that lets you upload PDF documents and ask natural-language questions about their content. It uses retrieval-augmented generation (RAG) to find relevant document passages before generating an answer with a configured language model.

## Features

- PDF upload through the Streamlit interface
- Text extraction with PyMuPDF, with an optional Unstructured fallback for image-based PDFs
- Recursive document chunking
- HuggingFace sentence embeddings
- FAISS similarity search
- Groq models with a Gemini fallback
- Conversational question answering during a session
- Retrieved source snippets with document names and page references
- Downloadable chat history
- A responsive Streamlit workspace with document status, suggested questions, and a dedicated chat interface

## Architecture

```text
PDF upload
    |
Text extraction
    |
Chunking
    |
Embeddings
    |
FAISS vector store
    |
Similarity retrieval
    |
Relevant context
    |
LLM
    |
Answer + sources
```

## Tech Stack

- Python
- Streamlit
- LangChain
- FAISS
- HuggingFace sentence-transformers
- PyMuPDF
- Unstructured (fallback extraction)
- Groq and Gemini language model integrations

## Project Structure

```text
DocQuery/
├── app.py
├── config.py
├── documents.py
├── llm.py
├── logging_utils.py
├── ui.py
├── vector_store.py
├── requirements.txt
├── .env.example
├── .gitignore
└── LICENSE
```

## Setup

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux or macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

Set at least one provider key before asking questions:

- `GROQ_API_KEY` enables the Groq models listed in the application.
- `GEMINI_API_KEY` enables the Gemini fallback.

The application loads keys from the local `.env` file, environment variables, or Streamlit secrets.

## Usage

Start the application:

```bash
streamlit run app.py
```

Then:

1. Add one or more PDFs in the dashboard upload area (or use **Upload PDF** in the sidebar to jump to it).
2. Wait for extraction, chunking, embedding, and FAISS indexing to finish.
3. Choose a suggested prompt or ask a question in the chat.
4. Review the answer and expand **View source passages** to inspect retrieved content and page references.

The index is rebuilt from the current upload, and the chat history remains available for the current Streamlit session.