from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import datetime as dt
import models, schemas
from database import get_db
from auth import require_roles, get_current_user
from services import interview_agent, knowledge_extraction, sop_generator, vector_store, graph_store

router = APIRouter(prefix="/interview", tags=["interview"])


@router.post("/start", response_model=schemas.InterviewOut)
def start_interview(
    payload: schemas.InterviewStart,
    db: Session = Depends(get_db),
    employee: models.User = Depends(require_roles("employee")),
):
    """Self-service: an employee starts their own knowledge-capture interview.
    Admins do not conduct interviews - they only review the resulting SOPs."""
    dept = db.query(models.Department).filter(models.Department.id == payload.department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    interview = models.Interview(
        employee_id=employee.id,
        candidate_name=payload.candidate_name,
        department_id=payload.department_id,
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)

    opening_question = interview_agent.get_opening_question(dept.name)
    msg = models.TranscriptMessage(interview_id=interview.id, role="ai", content=opening_question)
    db.add(msg)
    db.commit()

    return interview


@router.get("/{interview_id}", response_model=schemas.InterviewOut)
def get_interview(interview_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if user.role != "admin" and interview.employee_id != user.id:
        raise HTTPException(status_code=403, detail="Not your interview")
    return interview


@router.get("/{interview_id}/messages", response_model=List[schemas.MessageOut])
def get_messages(interview_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if user.role != "admin" and interview.employee_id != user.id:
        raise HTTPException(status_code=403, detail="Not your interview")
    return (
        db.query(models.TranscriptMessage)
        .filter(models.TranscriptMessage.interview_id == interview_id)
        .order_by(models.TranscriptMessage.created_at)
        .all()
    )


@router.post("/{interview_id}/answer")
def submit_answer(
    interview_id: str,
    payload: schemas.InterviewAnswer,
    db: Session = Depends(get_db),
    employee: models.User = Depends(require_roles("employee")),
):
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if interview.employee_id != employee.id:
        raise HTTPException(status_code=403, detail="Not your interview")
    if interview.status != "in_progress":
        raise HTTPException(status_code=400, detail="Interview is already finished")

    db.add(models.TranscriptMessage(interview_id=interview_id, role="employee", content=payload.answer))
    db.commit()

    messages = (
        db.query(models.TranscriptMessage)
        .filter(models.TranscriptMessage.interview_id == interview_id)
        .order_by(models.TranscriptMessage.created_at)
        .all()
    )
    transcript = [{"role": m.role, "content": m.content} for m in messages]
    questions_asked = sum(1 for m in messages if m.role == "ai")

    dept = db.query(models.Department).filter(models.Department.id == interview.department_id).first()
    next_question, is_closing = interview_agent.generate_next_question(dept.name, transcript, questions_asked)

    if is_closing:
        db.add(models.TranscriptMessage(
            interview_id=interview_id, role="ai", content=interview_agent.CLOSING_MESSAGE
        ))
        interview.status = "completed"
        interview.completed_at = dt.datetime.utcnow()
        interview.completeness_score = interview_agent.score_completeness(transcript)
        db.commit()

        # Immediately extract knowledge + generate the SOP + publish to the Twin's
        # retrieval system. No separate manager-approval step in this workflow -
        # the moment an interview finishes, its SOP becomes part of the AI Twin's
        # knowledge base for that department.
        result = _finalize_interview(db, interview, transcript)
        return {
            "finished": True,
            "completeness_score": interview.completeness_score,
            "closing_message": interview_agent.CLOSING_MESSAGE,
            "sop": result,
        }

    db.add(models.TranscriptMessage(interview_id=interview_id, role="ai", content=next_question))
    db.commit()
    return {"finished": False, "next_question": next_question}


def _finalize_interview(db: Session, interview: models.Interview, transcript: list[dict]):
    extracted = knowledge_extraction.extract_knowledge(transcript)
    sop = sop_generator.generate_sop(extracted)

    employee = db.query(models.User).filter(models.User.id == interview.employee_id).first()
    dept = db.query(models.Department).filter(models.Department.id == interview.department_id).first()

    chunk = models.KnowledgeChunk(
        interview_id=interview.id,
        department_id=interview.department_id,
        chunk_type="summary",
        content=extracted.get("summary", ""),
    )
    db.add(chunk)

    sop_row = models.SOP(
        interview_id=interview.id,
        department_id=interview.department_id,
        title=sop.get("title", "Untitled SOP"),
        purpose=sop.get("purpose", ""),
        prerequisites=sop.get("prerequisites", ""),
        procedure=sop.get("procedure", ""),
        validation=sop.get("validation", ""),
        escalation=sop.get("escalation", ""),
        risk_mitigation=sop.get("risk_mitigation", ""),
        status="approved",
    )
    db.add(sop_row)

    # Persist skills for the admin knowledge graph (department relatedness via shared skills)
    for skill in extracted.get("skills", []):
        db.add(models.KnowledgeSkill(
            interview_id=interview.id, department_id=interview.department_id, skill_name=skill.strip().lower()
        ))

    db.commit()
    db.refresh(sop_row)

    # ---- RAG STEP: push the finalized SOP into ChromaDB so the AI Twin can retrieve it ----
    # Per design: the Twin answers ONLY from approved, structured SOPs - not raw
    # interview summaries - so every answer is grounded in a reviewed, complete document.
    vector_store.add_document(
        doc_id=f"sop-{sop_row.id}",
        text=f"{sop_row.title}\n\nPurpose: {sop_row.purpose}\n\nProcedure: {sop_row.procedure}\n\nValidation: {sop_row.validation}\n\nEscalation: {sop_row.escalation}\n\nRisk Mitigation: {sop_row.risk_mitigation}",
        metadata={"department_id": interview.department_id, "type": "sop", "sop_id": sop_row.id, "sop_title": sop_row.title},
    )

    # Optional graph layer (no-op if Neo4j isn't configured)
    for skill in extracted.get("skills", []):
        graph_store.add_employee_skill(employee.name, dept.name, skill)
    for problem in extracted.get("troubleshooting_steps", [])[:1]:
        graph_store.add_solution(employee.name, problem, extracted.get("summary", ""), sop_row.title)

    return schemas.SOPOut.model_validate(sop_row)
