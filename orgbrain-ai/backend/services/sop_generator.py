"""
Generates a detailed, structured SOP document from extracted interview knowledge.
This SOP becomes the single source of truth the AI Twin (RAG) retrieves from -
so it's written to be thorough and self-contained, not just a short summary.
"""
from services.llm_provider import call_llm, safe_json_parse

SOP_SYSTEM_PROMPT = """You write detailed, professional Standard Operating Procedures (SOPs)
for an internal company knowledge base. These SOPs are the ONLY source of truth an AI
assistant will use to answer future employees' questions, so be thorough, specific, and
self-contained - do not assume any other context is available. Given extracted interview
knowledge, produce ONLY a JSON object with this exact shape, no markdown fences, no extra text:

{
  "title": "Short, specific SOP title",
  "purpose": "2-3 sentences on why this SOP exists and what problem it addresses",
  "prerequisites": "Access, tools, credentials, or background knowledge needed",
  "procedure": "A detailed, numbered, step-by-step procedure written in full sentences. Be specific - include exact steps, not vague generalities.",
  "validation": "How to confirm the procedure worked / issue is resolved",
  "escalation": "Who or what to contact if this doesn't resolve the issue",
  "risk_mitigation": "Known risks, common mistakes to avoid, and how to mitigate them"
}
"""


def generate_sop(extracted_knowledge: dict) -> dict:
    user_prompt = (
        f"Extracted knowledge from the interview:\n"
        f"Summary: {extracted_knowledge.get('summary')}\n"
        f"Skills: {extracted_knowledge.get('skills')}\n"
        f"Technologies: {extracted_knowledge.get('technologies')}\n"
        f"Best practices: {extracted_knowledge.get('best_practices')}\n"
        f"Troubleshooting steps: {extracted_knowledge.get('troubleshooting_steps')}\n"
        f"Common mistakes: {extracted_knowledge.get('common_mistakes')}\n"
        f"Recommendations: {extracted_knowledge.get('recommendations')}\n"
    )
    raw = call_llm(SOP_SYSTEM_PROMPT, user_prompt, json_mode=True)
    parsed = safe_json_parse(raw)
    defaults = {
        "title": "Untitled SOP", "purpose": "", "prerequisites": "",
        "procedure": "", "validation": "", "escalation": "", "risk_mitigation": "",
    }
    defaults.update({k: v for k, v in parsed.items() if k in defaults})
    return defaults
