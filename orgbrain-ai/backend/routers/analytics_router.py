from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
from database import get_db
from auth import get_current_user
from services import graph_store

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def overview(db: Session = Depends(get_db), user=Depends(get_current_user)):
    total_interviews = db.query(func.count(models.Interview.id)).scalar()
    completed_interviews = db.query(func.count(models.Interview.id)).filter(models.Interview.status.in_(["completed", "approved"])).scalar()
    avg_completeness = db.query(func.avg(models.Interview.completeness_score)).scalar() or 0
    total_sops = db.query(func.count(models.SOP.id)).filter(models.SOP.status == "approved").scalar()
    total_twin_queries = db.query(func.count(models.TwinQueryLog.id)).scalar()
    departments = db.query(func.count(models.Department.id)).scalar()

    return {
        "total_interviews": total_interviews,
        "completed_interviews": completed_interviews,
        "avg_completeness_score": round(avg_completeness, 1),
        "total_sops_published": total_sops,
        "total_twin_queries": total_twin_queries,
        "departments_covered": departments,
        "graph_stats": graph_store.graph_stats(),
    }


@router.get("/department/{department_id}")
def department_analytics(department_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    interviews = db.query(models.Interview).filter(models.Interview.department_id == department_id).count()
    sops = db.query(models.SOP).filter(models.SOP.department_id == department_id, models.SOP.status == "approved").count()
    avg_score = db.query(func.avg(models.Interview.completeness_score)).filter(models.Interview.department_id == department_id).scalar() or 0
    queries = db.query(func.count(models.TwinQueryLog.id)).filter(models.TwinQueryLog.department_id == department_id).scalar()

    return {
        "department_id": department_id,
        "interviews": interviews,
        "sops_published": sops,
        "avg_completeness_score": round(avg_score, 1),
        "twin_queries": queries,
    }
