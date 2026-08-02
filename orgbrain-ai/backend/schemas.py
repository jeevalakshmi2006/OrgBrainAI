from pydantic import BaseModel, EmailStr
from typing import Optional, List
import datetime as dt

# ---- Auth ----
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    name: str

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "employee"
    department_id: Optional[str] = None

class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: str
    department_id: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

# ---- Department ----
class DepartmentCreate(BaseModel):
    name: str
    description: str = ""

class DepartmentOut(BaseModel):
    id: str
    name: str
    description: str

    class Config:
        from_attributes = True

# ---- Interview ----
class InterviewStart(BaseModel):
    candidate_name: str
    department_id: str

class InterviewAnswer(BaseModel):
    answer: str

class MessageOut(BaseModel):
    role: str
    content: str

    class Config:
        from_attributes = True

class InterviewOut(BaseModel):
    id: str
    employee_id: str
    candidate_name: str
    department_id: str
    status: str
    completeness_score: float

    class Config:
        from_attributes = True

class AdminInterviewOut(BaseModel):
    id: str
    candidate_name: str
    department_name: str
    status: str
    completeness_score: float
    sop_id: Optional[str] = None
    created_at: dt.datetime

# ---- Twin Chat ----
class TwinChatRequest(BaseModel):
    department_id: str
    question: str

class TwinChatResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[dict]

# ---- Knowledge Graph (admin dashboard) ----
class GraphNode(BaseModel):
    id: str
    name: str
    knowledge_count: int

class GraphEdge(BaseModel):
    source: str
    target: str
    weight: int

class KnowledgeGraphOut(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

# ---- SOP ----
class SOPOut(BaseModel):
    id: str
    title: str
    purpose: str
    prerequisites: str
    procedure: str
    validation: str
    escalation: str
    risk_mitigation: str
    status: str

    class Config:
        from_attributes = True
