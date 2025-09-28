"""
LLM wrapper + Chatbot behavior.

Supports three modes:
 - openai (using openai package)
 - azure_openai (using azure.ai.openai style; we use simple REST wrapper to keep dependency optional)
 - rule_based (offline fallback)

Priority and auto-detection:
 - If OPENAI_API_KEY present -> openai
 - Else if AZURE_OPENAI_KEY & AZURE_OPENAI_ENDPOINT present -> azure_openai
 - Else -> rule_based

Chatbot class manages conversation context and last generated questions.
"""

import os
import time
import json
from typing import List, Dict, Any
from prompts import question_prompt_template
from dotenv import load_dotenv
load_dotenv()

# Try to import optional packages; if not available, rule_based will still work.
try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

# NOTE: We don't import azure SDK by default to keep local runs simple.
# The wrapper will use requests if Azure OpenAI is configured (lightweight approach).
import requests

# Simple fallback rule-based question generator
RULE_BASED_QUESTION_BANK = {
    "python": [
        "Explain the difference between a list and a tuple in Python.",
        "How does Python's GIL affect multi-threaded programs?",
        "Write a function to reverse a string and explain its complexity."
    ],
    "django": [
        "What is Django's MTV architecture? How is it different from MVC?",
        "How do you manage database migrations in Django?",
        "Explain middlewares in Django and a use-case for creating a custom middleware."
    ],
    "react": [
        "What are React hooks and why were they introduced?",
        "Explain the difference between props and state in React.",
        "How does the virtual DOM work?"
    ],
    "sql": [
        "Write a SQL query to find duplicate rows in a table.",
        "Explain the difference between INNER JOIN and LEFT JOIN.",
        "What is indexing and how does it improve query performance?"
    ],
    "aws": [
        "What is IAM and why is it important?",
        "Describe how S3 versioning works and a use-case.",
        "Compare EC2 and Lambda for running compute workloads."
    ]
}

def simple_normalize_tech(tech_list: List[str]) -> List[str]:
    return [t.strip().lower() for t in tech_list if t and isinstance(t, str)]

class LLMWrapper:
    def __init__(self):
        # detect provider
        self.provider = os.getenv("FORCE_PROVIDER", "").lower() or "auto"
        openai_key = os.getenv("OPENAI_API_KEY")
        azure_key = os.getenv("AZURE_OPENAI_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if self.provider == "auto":
            if openai_key:
                self.provider = "openai"
            elif azure_key and azure_endpoint:
                self.provider = "azure_openai"
            else:
                self.provider = "rule_based"

        # configure clients lightly
        if self.provider == "openai" and OPENAI_AVAILABLE:
            openai.api_key = openai_key
        self.openai_available = OPENAI_AVAILABLE
        self.azure_endpoint = azure_endpoint
        self.azure_key = azure_key

    def generate(self, prompt: str, max_tokens: int = 300) -> str:
        """
        Single method to get a textual completion from selected provider.
        """
        if self.provider == "openai" and self.openai_available:
            try:
                resp = openai.Completion.create(
                    engine=os.getenv("OPENAI_ENGINE", "text-davinci-003"),
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=0.2,
                    n=1,
                    stop=None
                )
                return resp.choices[0].text.strip()
            except Exception as e:
                # fallback to rule_based on failure
                print("OpenAI error:", e)
                return self._rule_based_from_prompt(prompt)
        elif self.provider == "azure_openai" and self.azure_key and self.azure_endpoint:
            try:
                url = self.azure_endpoint.rstrip("/") + "/openai/deployments/" + os.getenv("AZURE_OPENAI_DEPLOYMENT", "text-davinci-003") + "/completions?api-version=2023-05-15"
                headers = {"api-key": self.azure_key, "Content-Type": "application/json"}
                payload = {"prompt": prompt, "max_tokens": max_tokens, "temperature": 0.2}
                r = requests.post(url, headers=headers, json=payload, timeout=10)
                r.raise_for_status()
                data = r.json()
                # Azure response shape is similar: choices[0].text
                return data["choices"][0]["text"].strip()
            except Exception as e:
                print("Azure OpenAI error:", e)
                return self._rule_based_from_prompt(prompt)
        else:
            # rule-based or default
            return self._rule_based_from_prompt(prompt)

    def _rule_based_from_prompt(self, prompt: str) -> str:
        # Very light heuristic: extract tech names from prompt and produce canned Qs.
        # If can't, return a helpful fallback message.
        lower = prompt.lower()
        matched = []
        for tech in RULE_BASED_QUESTION_BANK.keys():
            if tech in lower:
                matched.append(tech)
        if not matched:
            # attempt to find keywords after 'tech:' or 'stack:'
            return ("I couldn't use an LLM backend. Here's a helpful fallback: "
                    "Please list your tech stack (e.g., Python, Django, React). "
                    "I can generate technical questions once you provide technologies.")
        questions = []
        for tech in matched:
            questions.extend(RULE_BASED_QUESTION_BANK.get(tech, [])[:3])
        # return as numbered list
        return "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))

class Chatbot:
    """
    Encapsulates conversational logic, prompts, history and fallback handling.
    """
    def __init__(self, llm: LLMWrapper):
        self.llm = llm
        self.context = []  # optional context storage for future
        self.last_generated_questions = []

    def greeting(self) -> str:
        return ("Hi — I'm TalentScout, your hiring assistant. "
                "I will collect a few details and generate 3–5 technical questions per technology you list. "
                "Type 'done' or 'exit' to finish the conversation.")

    def farewell(self) -> str:
        return ("Thanks! Your session is complete. We'll anonymize and store non-sensitive details. "
                "Good luck!")

    def handle_message(self, message: str, candidate: Dict[str, Any]) -> str:
        # Basic routing: if message asks for questions or tech stack supplied -> generate Qs
        mlow = message.strip().lower()
        if any(token in mlow for token in ["generate", "questions", "ask me", "screening"]):
            techs = candidate.get("tech_stack", [])
            if not techs:
                return "Please provide your tech stack (comma-separated) so I can generate questions."
            return self.generate_questions_for_stack(techs)
        # If user provides a list of techs in chat, attempt to parse it
        if "," in message and len(message.split(",")) <= 10 and len(message.split()) < 50:
            # treat as tech list
            techs = [t.strip() for t in message.split(",") if t.strip()]
            return self.generate_questions_for_stack(techs)
        # fallback small talk or clarification
        if len(message.strip()) < 3:
            return "Could you please elaborate? If you'd like, provide your tech stack or ask me to 'generate questions'."
        return "I didn't quite understand — you can either update the candidate form, provide your tech stack (e.g., 'Python, React'), or ask me to 'generate questions'."

    def generate_questions_for_stack(self, techs: List[str]) -> str:
        techs_norm = simple_normalize_tech(techs)
        # craft prompt (uses prompts.question_prompt_template)
        prompt = question_prompt_template(techs_norm, num_questions_per_tech=3)
        response = self.llm.generate(prompt, max_tokens=400)
        # If LLM returns a long text with questions, parse into list heuristically
        parsed_questions = self._parse_questions(response)
        self.last_generated_questions = parsed_questions
        if parsed_questions:
            out = "Here are the generated technical questions:\n" + "\n".join(f"{i+1}. {q}" for i, q in enumerate(parsed_questions))
            return out
        # fallback
        return response

    def _parse_questions(self, text: str) -> List[str]:
        # Try to split on lines with numbering, or bullets
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        questions = []
        for line in lines:
            # remove leading numbers/bullets
            cleaned = line
            if cleaned.lstrip().startswith(("-", "*")):
                cleaned = cleaned.lstrip("-* ").strip()
            # common numbering formats
            for sep in (". ", ") ", " - "):
                if sep in cleaned and cleaned.split(sep)[0].isdigit():
                    cleaned = sep.join(cleaned.split(sep)[1:]).strip()
            # heuristics: discard lines that are too short
            if len(cleaned) > 10:
                questions.append(cleaned)
        # Limit total questions to 15 (safety)
        return questions[:15]
