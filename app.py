"""
Streamlit front-end for TalentScout Hiring Assistant.

Run locally:
    streamlit run app.py

This app uses chatbot_logic.py for LLM/question generation and utils_storage.py
to save anonymized candidate JSON locally or to Azure Blob Storage (if configured).
"""

import streamlit as st
from dotenv import load_dotenv
import os
from chatbot_logic import LLMWrapper, Chatbot
from utils_storage import save_local_candidate, try_upload_to_azure
from generate_dummy_data import generate_dummy_candidate
from datetime import datetime

# Load environment variables from .env (if present)
load_dotenv()

EXIT_KEYWORDS = {"exit", "quit", "bye", "done"}

st.set_page_config(page_title="TalentScout Hiring Assistant", layout="centered")

# Initialize session state for chat history & candidate
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of (role, text)
if "candidate" not in st.session_state:
    st.session_state.candidate = {}
if "llm" not in st.session_state:
    # Create LLM wrapper instance and Chatbot
    st.session_state.llm = LLMWrapper()
if "chatbot" not in st.session_state:
    st.session_state.chatbot = Chatbot(st.session_state.llm)

def add_message(role: str, text: str):
    st.session_state.messages.append((role, text))

def show_chat():
    for role, text in st.session_state.messages:
        if role == "assistant":
            st.markdown(f"**Assistant:** {text}")
        else:
            st.markdown(f"**User:** {text}")

def collect_candidate_info():
    st.header("Candidate Info")
    with st.form("candidate_form"):
        full_name = st.text_input("Full name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        years_exp = st.number_input("Years of experience", min_value=0.0, max_value=50.0, value=1.0, step=0.5)
        desired_positions = st.text_input("Desired position(s) (comma-separated)")
        location = st.text_input("Current location (city/country)")
        tech_stack = st.text_area("Tech stack (comma-separated; e.g. Python, Django, React, SQL)")
        submitted = st.form_submit_button("Start Chat / Update Candidate")
    if submitted:
        st.session_state.candidate = {
            "full_name": full_name.strip(),
            "email": email.strip(),
            "phone": phone.strip(),
            "years_experience": float(years_exp),
            "desired_positions": [p.strip() for p in desired_positions.split(",") if p.strip()],
            "location": location.strip(),
            "tech_stack": [t.strip() for t in tech_stack.split(",") if t.strip()],
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        add_message("user", f"Candidate registered: {st.session_state.candidate.get('full_name') or 'N/A'}")
        add_message("assistant", st.session_state.chatbot.greeting())

def input_area():
    st.header("Chat")
    user_input = st.text_input("Type your message here (or type exit/quit/done to finish):", key="user_input")
    if st.button("Send"):
        if not user_input:
            st.warning("Please type something or use the candidate form.")
            return
        if user_input.strip().lower() in EXIT_KEYWORDS:
            add_message("user", user_input)
            add_message("assistant", st.session_state.chatbot.farewell())
            st.experimental_rerun()
        add_message("user", user_input)
        # process message with chatbot
        response = st.session_state.chatbot.handle_message(user_input, st.session_state.candidate)
        add_message("assistant", response)
        # optionally save candidate after question generation
        if st.session_state.chatbot.last_generated_questions:
            # anonymize before saving: remove email/phone if present or mask them
            candidate_copy = dict(st.session_state.candidate)
            # mask email/phone optionally
            if candidate_copy.get("email"):
                candidate_copy["email"] = "redacted@example.com"
            if candidate_copy.get("phone"):
                candidate_copy["phone"] = "REDACTED"
            candidate_copy["questions"] = st.session_state.chatbot.last_generated_questions
            save_local_candidate(candidate_copy)
            # attempt azure upload (no-op if not configured)
            try_upload_to_azure(candidate_copy)

def sidebar_controls():
    st.sidebar.title("Settings / Helpers")
    provider = st.sidebar.selectbox("LLM Provider (priority order enforced in code)", ["auto-detect", "openai", "azure_openai", "rule_based"])
    st.sidebar.write("Provider chosen controls which backend is attempted first. 'auto-detect' respects env vars.")
    st.sidebar.button("Generate dummy candidate", key="gen_dummy", on_click=generate_dummy_and_fill)

def generate_dummy_and_fill():
    dummy = generate_dummy_candidate()
    st.session_state.candidate = dummy
    add_message("assistant", "Filled candidate form with dummy data (for testing).")
    st.experimental_rerun()

def main():
    st.title("TalentScout — Hiring Assistant (LLM-powered)")
    st.write("Hello! I'm TalentScout — I collect basic candidate info and generate technical screening questions.")
    sidebar_controls()
    collect_candidate_info()
    input_area()
    st.markdown("---")
    st.subheader("Conversation")
    show_chat()
    st.markdown("---")
    st.caption("Data stored locally unless Azure Blob Storage is configured via environment variables.")

if __name__ == "__main__":
    main()
