"""Small logging adapter for file logs and Streamlit session status."""

import datetime
import logging

import streamlit as st

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def log_event(message: str, level: str = "INFO") -> None:
    """Write an event to the application log and current Streamlit session."""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_method = getattr(logging, level.lower(), logging.info)
    log_method(message)

    entries = st.session_state.setdefault("app_logs", [])
    entries.insert(0, f"[{timestamp}] {message}")
    del entries[100:]