"""
Adaptive Interview Agent.
Uses an LLM to (1) ask the next question given history, (2) score knowledge
completeness. Guarantees a minimum of MIN_QUESTIONS before it's allowed to
end, and always closes with a thank-you message once finished.
"""
from services.llm_provider import call_llm, safe_json_parse

QUESTION_BANKS = {
    "Software Development": [
        "Describe a production outage you handled and how you resolved it.",
        "What architecture decisions had the biggest long-term impact on your team's codebase?",
        "How do you approach debugging distributed systems?",
        "What deployment mistakes have you seen junior developers make?",
        "Explain your rollback strategy when a deployment fails.",
        "What tools or scripts have you built that others on the team now depend on?",
    ],
    "Software Testing": [
        "Walk me through how you triage a newly reported defect.",
        "How do you prioritize bugs during release week?",
        "Describe a regression that reached production despite testing.",
        "How do you design test coverage for high-risk modules?",
        "What's a testing best practice you wish new hires learned on day one?",
        "How do you decide when a feature is 'safe enough' to ship?",
    ],
    "IT Marketing": [
        "Walk me through your product launch process end-to-end.",
        "How do you plan and measure a marketing campaign?",
        "How do you measure customer acquisition efficiency?",
        "Describe your crisis communication procedure.",
        "What channel consistently outperformed expectations, and why?",
        "What's a campaign mistake that taught your team something valuable?",
    ],
}

DEFAULT_QUESTIONS = [
    "Describe the most important responsibility in your role.",
    "What is a mistake you made early on that taught you something important?",
    "What would you want your replacement to know on day one?",
    "What's a recurring problem in your work, and how do you usually solve it?",
    "What tools, processes, or shortcuts make your work easier?",
    "What's one thing about your role that isn't written down anywhere?",
]

MIN_QUESTIONS = 6
MAX_QUESTIONS = 8
COMPLETENESS_THRESHOLD = 80.0
CLOSING_MESSAGE = (
    "Thank you so much for sharing your knowledge and experience — this has been "
    "captured and will help your colleagues for a long time to come. Your responses "
    "are now being organized into a structured knowledge document."
)


def get_opening_question(department_name: str) -> str:
    bank = QUESTION_BANKS.get(department_name, DEFAULT_QUESTIONS)
    return bank[0]


def score_completeness(transcript: list[dict]) -> float:
    convo = "\n".join(f"{m['role']}: {m['content']}" for m in transcript)
    system = (
        "You are an expert knowledge-capture evaluator. Score how completely the "
        "employee's answers cover: technical depth, decision rationale, "
        "troubleshooting knowledge, best practices, lessons learned, and process "
        "knowledge. Return ONLY a JSON object: {\"score\": <0-100 number>}."
    )
    raw = call_llm(system, convo, json_mode=True)
    parsed = safe_json_parse(raw)
    try:
        return float(parsed.get("score", 0))
    except (TypeError, ValueError):
        return 0.0


def generate_next_question(department_name: str, transcript: list[dict], questions_asked: int):
    """Returns (question_or_none, is_closing_message).
    Returns (None, True) once the interview should end - caller should
    treat that as: interview finished, CLOSING_MESSAGE already appended."""
    bank = QUESTION_BANKS.get(department_name, DEFAULT_QUESTIONS)

    if questions_asked < MIN_QUESTIONS:
        # Always keep going until the minimum is hit, regardless of completeness.
        pass
    else:
        completeness = score_completeness(transcript)
        if completeness >= COMPLETENESS_THRESHOLD or questions_asked >= MAX_QUESTIONS:
            return None, True

    convo = "\n".join(f"{m['role']}: {m['content']}" for m in transcript)
    remaining_bank_questions = bank[questions_asked:] if questions_asked < len(bank) else []

    system = (
        f"You are conducting a knowledge-preservation interview for the {department_name} "
        "department. Based on the conversation so far, ask ONE natural follow-up question "
        "that digs deeper into whatever is missing (technical detail, reasoning, "
        "troubleshooting steps, or lessons learned). Keep it to a single question, "
        "conversational, no preamble, no numbering. "
        f"If helpful, draw inspiration from this bank of topic questions: {remaining_bank_questions}"
    )
    question = call_llm(system, convo, json_mode=False)
    return question.strip(), False
