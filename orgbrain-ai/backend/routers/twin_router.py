from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from auth import get_current_user
from services import vector_store, graph_store
from services.llm_provider import call_llm

router = APIRouter(prefix="/twin", tags=["twin"])

TWIN_SYSTEM_PROMPT = """You are a Department AI Twin - an assistant that answers employee
questions using ONLY the retrieved Standard Operating Procedures (SOPs) provided below as
context. These SOPs are the department's complete, reviewed knowledge base, captured from
real employee interviews. If the context does not contain a relevant answer, say so honestly
rather than guessing or using outside knowledge. Reference which SOP each part of your answer
comes from. Be concise, practical, and specific."""


@router.post("/chat", response_model=schemas.TwinChatResponse)
def twin_chat(
    payload: schemas.TwinChatRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    retrieved = vector_store.query(payload.question, department_id=payload.department_id, top_k=5)

    if not retrieved:
        answer = (
            "I don't have any approved organizational knowledge for this department yet "
            "to ground an answer in. Once interviews are conducted and approved, I'll be "
            "able to answer this from real historical knowledge."
        )
        confidence = 0.0
        sources = []
    else:
        context_text = "\n\n".join(f"[Source: {r['metadata'].get('type', 'unknown')}] {r['text']}" for r in retrieved)
        user_prompt = f"Context:\n{context_text}\n\nQuestion: {payload.question}"
        answer = call_llm(TWIN_SYSTEM_PROMPT, user_prompt, json_mode=False)
        # naive confidence: based on how close the closest match was (lower distance = better)
        best_distance = min((r["distance"] for r in retrieved if r["distance"] is not None), default=1.0)
        confidence = max(0.0, min(1.0, 1.0 - best_distance))
        sources = [{"type": r["metadata"].get("type"), "metadata": r["metadata"]} for r in retrieved]

    log = models.TwinQueryLog(
        department_id=payload.department_id,
        user_id=user.id,
        question=payload.question,
        answer=answer,
        confidence=confidence,
    )
    db.add(log)
    db.commit()

    return schemas.TwinChatResponse(answer=answer, confidence=confidence, sources=sources)


@router.get("/experts")
def find_experts(skill: str, user: models.User = Depends(get_current_user)):
    """Graph-powered expert lookup. Returns [] gracefully if Neo4j isn't configured."""
    experts = graph_store.find_experts_by_skill(skill)
    return {"skill": skill, "experts": experts, "graph_enabled": graph_store.is_enabled()}
