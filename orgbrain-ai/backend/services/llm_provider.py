"""
LLM Provider abstraction.
Swap providers by changing LLM_PROVIDER in .env - no other code changes needed.
Supported: groq | huggingface | gemini
"""
import httpx
import json
from config import settings


def call_llm(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    provider = settings.LLM_PROVIDER.lower()
    try:
        if provider == "groq":
            return _call_groq(system_prompt, user_prompt, json_mode)
        elif provider == "huggingface":
            return _call_huggingface(system_prompt, user_prompt, json_mode)
        elif provider == "gemini":
            return _call_gemini(system_prompt, user_prompt, json_mode)
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {provider}")
    except httpx.HTTPStatusError as e:
        raise RuntimeError(
            f"LLM provider '{provider}' rejected the request (HTTP {e.response.status_code}). "
            f"Check that {provider.upper()}_API_KEY in backend/.env is a real, valid key, "
            f"and that LLM_PROVIDER matches the key you filled in."
        ) from e
    except httpx.RequestError as e:
        raise RuntimeError(
            f"Could not reach the '{provider}' API - check your internet connection."
        ) from e


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    with httpx.Client(timeout=60) as client:
        resp = client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()
    return data["choices"][0]["message"]["content"]


def _call_huggingface(system_prompt: str, user_prompt: str, json_mode: bool) -> str:
    # Uses HF Inference Router (OpenAI-compatible) - works with IBM Granite, Llama, etc.
    url = "https://router.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.HF_API_KEY}",
        "Content-Type": "application/json",
    }
    full_prompt = user_prompt
    if json_mode:
        full_prompt += "\n\nRespond with ONLY valid JSON, no markdown fences, no preamble."
    body = {
        "model": settings.HF_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_prompt},
        ],
        "temperature": 0.3,
    }
    with httpx.Client(timeout=60) as client:
        resp = client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()
    return data["choices"][0]["message"]["content"]


def _call_gemini(system_prompt: str, user_prompt: str, json_mode: bool) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
    body = {
        "contents": [{"parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {"temperature": 0.3},
    }
    if json_mode:
        body["generationConfig"]["responseMimeType"] = "application/json"
    with httpx.Client(timeout=60) as client:
        resp = client.post(url, json=body)
        resp.raise_for_status()
        data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def safe_json_parse(text: str) -> dict:
    """Strip markdown fences if a model adds them despite instructions, then parse."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"raw": text}
