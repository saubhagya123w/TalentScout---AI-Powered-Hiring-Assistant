"""
Prompt templates used by the LLM wrapper.

Keep templates concise and instructive to guide the model to:
 - Generate 3-5 technical questions per technology
 - Keep each question clear, concise, and of moderate difficulty for initial screening
"""

from typing import List

def question_prompt_template(techs: List[str], num_questions_per_tech: int = 3) -> str:
    techs_joined = ", ".join(techs)
    # Instruct the model clearly and provide format constraints
    return (
        f"You are a hiring-assistant that generates short technical screening questions.\n"
        f"Candidate tech-stack: {techs_joined}\n"
        f"Task: For each technology listed, produce {num_questions_per_tech} concise, clear, and varied screening questions "
        f"(conceptual, short coding/design, and troubleshooting/ops where applicable). "
        f"Number each question and label which technology it is for. "
        f"Do not ask for personal data. Keep each question under 40 words.\n\n"
        f"Output format example:\n"
        f"1. [Python] Explain ...\n"
        f"2. [Django] How would you ...\n\n"
        f"Begin generating now."
    )
