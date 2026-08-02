from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import io
from fpdf import FPDF
import models, schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/sop", tags=["sop"])


@router.get("/search", response_model=List[schemas.SOPOut])
def search_sops(
    department_id: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    query = db.query(models.SOP).filter(models.SOP.status == "approved")
    if department_id:
        query = query.filter(models.SOP.department_id == department_id)
    if q:
        like = f"%{q}%"
        query = query.filter(models.SOP.title.ilike(like))
    return query.order_by(models.SOP.created_at.desc()).all()


@router.get("/{sop_id}", response_model=schemas.SOPOut)
def get_sop(sop_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sop = db.query(models.SOP).filter(models.SOP.id == sop_id).first()
    if not sop:
        raise HTTPException(status_code=404, detail="SOP not found")
    return sop


def _build_pdf(sop: models.SOP, department_name: str, candidate_name: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(15, 41, 66)  # navy
    pdf.multi_cell(0, 10, sop.title)
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 6, f"Department: {department_name}   |   Source Interview: {candidate_name}")
    pdf.ln(4)

    sections = [
        ("Purpose", sop.purpose),
        ("Prerequisites", sop.prerequisites),
        ("Procedure", sop.procedure),
        ("Validation", sop.validation),
        ("Escalation", sop.escalation),
        ("Risk Mitigation", sop.risk_mitigation),
    ]
    for heading, body in sections:
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(59, 110, 165)  # steel
        pdf.cell(0, 8, heading, ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(30, 30, 30)
        pdf.multi_cell(0, 6, body or "-")
        pdf.ln(3)

    return bytes(pdf.output())


@router.get("/{sop_id}/pdf")
def download_sop_pdf(sop_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sop = db.query(models.SOP).filter(models.SOP.id == sop_id).first()
    if not sop:
        raise HTTPException(status_code=404, detail="SOP not found")
    department = db.query(models.Department).filter(models.Department.id == sop.department_id).first()
    candidate_name = "Unknown"
    if sop.interview_id:
        interview = db.query(models.Interview).filter(models.Interview.id == sop.interview_id).first()
        if interview:
            candidate_name = interview.candidate_name

    pdf_bytes = _build_pdf(sop, department.name if department else "Unknown", candidate_name)
    filename = "".join(c if c.isalnum() or c in " -_" else "" for c in sop.title).strip().replace(" ", "_") or "SOP"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}.pdf"'},
    )
