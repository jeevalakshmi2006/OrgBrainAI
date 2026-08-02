from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from collections import defaultdict
from itertools import combinations
import models, schemas
from database import get_db
from auth import require_roles, get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[schemas.UserOut])
def list_users(db: Session = Depends(get_db), admin=Depends(require_roles("admin"))):
    return db.query(models.User).all()


@router.patch("/users/{user_id}/deactivate", response_model=schemas.UserOut)
def deactivate_user(user_id: str, db: Session = Depends(get_db), admin=Depends(require_roles("admin"))):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.post("/departments", response_model=schemas.DepartmentOut)
def create_department(payload: schemas.DepartmentCreate, db: Session = Depends(get_db), admin=Depends(require_roles("admin"))):
    dept = models.Department(name=payload.name, description=payload.description)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.get("/departments", response_model=List[schemas.DepartmentOut])
def list_departments(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Open to all authenticated roles - needed for dropdowns across the app."""
    return db.query(models.Department).all()


@router.get("/interviews", response_model=List[schemas.AdminInterviewOut])
def list_interviews(db: Session = Depends(get_db), admin=Depends(require_roles("admin"))):
    """Everyone who has been interviewed, their department, and their SOP - for the admin dashboard."""
    interviews = db.query(models.Interview).order_by(models.Interview.created_at.desc()).all()
    results = []
    for interview in interviews:
        dept = db.query(models.Department).filter(models.Department.id == interview.department_id).first()
        sop = db.query(models.SOP).filter(models.SOP.interview_id == interview.id).first()
        results.append(schemas.AdminInterviewOut(
            id=interview.id,
            candidate_name=interview.candidate_name,
            department_name=dept.name if dept else "Unknown",
            status=interview.status,
            completeness_score=interview.completeness_score,
            sop_id=sop.id if sop else None,
            created_at=interview.created_at,
        ))
    return results


@router.get("/knowledge-graph", response_model=schemas.KnowledgeGraphOut)
def knowledge_graph(db: Session = Depends(get_db), admin=Depends(require_roles("admin"))):
    """
    Powers the animated knowledge graph on the admin dashboard.
    Nodes = departments, sized by how much knowledge (SOPs) has been collected.
    Edges = relatedness between departments, computed from skills that show up
    in more than one department's interviews (no Neo4j required for this view -
    it's a lightweight SQL aggregation, separate from the optional Neo4j layer
    used for expert lookup).
    """
    departments = db.query(models.Department).all()
    nodes = []
    dept_skill_map = defaultdict(set)

    for dept in departments:
        sop_count = db.query(func.count(models.SOP.id)).filter(
            models.SOP.department_id == dept.id, models.SOP.status == "approved"
        ).scalar()
        nodes.append(schemas.GraphNode(id=dept.id, name=dept.name, knowledge_count=sop_count))

        skills = db.query(models.KnowledgeSkill.skill_name).filter(
            models.KnowledgeSkill.department_id == dept.id
        ).distinct().all()
        dept_skill_map[dept.id] = {s[0] for s in skills}

    edges = []
    for (dept_a, dept_b) in combinations(dept_skill_map.keys(), 2):
        shared = dept_skill_map[dept_a] & dept_skill_map[dept_b]
        if shared:
            edges.append(schemas.GraphEdge(source=dept_a, target=dept_b, weight=len(shared)))

    return schemas.KnowledgeGraphOut(nodes=nodes, edges=edges)
