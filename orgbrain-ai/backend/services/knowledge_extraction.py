"""
Converts a raw interview transcript into structured organizational knowledge
using the LLM, then hands off to SOP generation + vector/graph storage.
"""
from services.llm_provider import call_llm, safe_json_parse

EXTRACTION_SYSTEM_PROMPT = """You are a knowledge extraction engine. Read the interview
transcript and extract structured organizational knowledge. Return ONLY a JSON object
with this exact shape, no markdown fences, no extra text:

{
  "skills": ["..."],
  "technologies": ["..."],
  "best_practices": ["..."],
  "troubleshooting_steps": ["..."],
  "common_mistakes": ["..."],
  "recommendations": ["..."],
  "summary": "2-3 sentence summary of the core knowledge captured"
}
"""


def extract_knowledge(transcript: list[dict]) -> dict:
    convo = "\n".join(f"{m['role']}: {m['content']}" for m in transcript)
    raw = call_llm(EXTRACTION_SYSTEM_PROMPT, convo, json_mode=True)
    parsed = safe_json_parse(raw)
    # Defensive defaults in case the model omits a field
    defaults = {
        "skills": [], "technologies": [], "best_practices": [],
        "troubleshooting_steps": [], "common_mistakes": [],
        "recommendations": [], "summary": "",
    }
    defaults.update({k: v for k, v in parsed.items() if k in defaults})
    return defaults
