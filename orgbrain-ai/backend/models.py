import uuid
import datetime as dt
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, Boolean, Integer
from sqlalchemy.orm import relationship
from database import Base

def gen_id():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="employee")  # admin | employee
    department_id = Column(String, ForeignKey("departments.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    department = relationship("Department", back_populates="users")


class Department(Base):
    __tablename__ = "departments"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    users = relationship("User", back_populates="department")
    interviews = relationship("Interview", back_populates="department")


class Interview(Base):
    __tablename__ = "interviews"
    id = Column(String, primary_key=True, default=gen_id)
    employee_id = Column(String, ForeignKey("users.id"), nullable=False)
    candidate_name = Column(String, nullable=False, default="")
    department_id = Column(String, ForeignKey("departments.id"), nullable=False)
    status = Column(String, default="in_progress")  # in_progress | completed
    completeness_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    department = relationship("Department", back_populates="interviews")
    messages = relationship("TranscriptMessage", back_populates="interview", cascade="all, delete-orphan")


class TranscriptMessage(Base):
    __tablename__ = "transcript_messages"
    id = Column(String, primary_key=True, default=gen_id)
    interview_id = Column(String, ForeignKey("interviews.id"), nullable=False)
    role = Column(String, nullable=False)  # ai | employee
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    interview = relationship("Interview", back_populates="messages")


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    id = Column(String, primary_key=True, default=gen_id)
    interview_id = Column(String, ForeignKey("interviews.id"), nullable=True)
    department_id = Column(String, ForeignKey("departments.id"), nullable=False)
    chunk_type = Column(String, default="summary")  # summary | best_practice | troubleshooting | mistake
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class SOP(Base):
    __tablename__ = "sops"
    id = Column(String, primary_key=True, default=gen_id)
    interview_id = Column(String, ForeignKey("interviews.id"), nullable=True)
    department_id = Column(String, ForeignKey("departments.id"), nullable=False)
    title = Column(String, nullable=False)
    purpose = Column(Text, default="")
    prerequisites = Column(Text, default="")
    procedure = Column(Text, default="")
    validation = Column(Text, default="")
    escalation = Column(Text, default="")
    risk_mitigation = Column(Text, default="")
    status = Column(String, default="pending_approval")  # pending_approval | approved
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class KnowledgeSkill(Base):
    """Denormalized skill records per department - powers the admin knowledge graph
    (department-to-department relatedness via shared skills) without requiring Neo4j."""
    __tablename__ = "knowledge_skills"
    id = Column(String, primary_key=True, default=gen_id)
    interview_id = Column(String, ForeignKey("interviews.id"), nullable=True)
    department_id = Column(String, ForeignKey("departments.id"), nullable=False)
    skill_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    details = Column(Text, default="")
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class TwinQueryLog(Base):
    __tablename__ = "twin_query_logs"
    id = Column(String, primary_key=True, default=gen_id)
    department_id = Column(String, ForeignKey("departments.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
