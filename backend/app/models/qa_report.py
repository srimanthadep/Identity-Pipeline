import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc).isoformat()

class QAReport(Base):
    __tablename__ = "qa_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    character_id = Column(String(36), ForeignKey("characters.id"), nullable=False)
    
    identity_score = Column(Float, nullable=True)
    appearance_score = Column(Float, nullable=True)
    decision = Column(String(30), nullable=False)  # 'PASS', 'FAIL', 'REVIEW'
    metrics = Column(Text, default="{}")  # JSON string
    
    reference_asset_uri = Column(String(500), nullable=True)
    evaluated_asset_uri = Column(String(500), nullable=True)
    is_simulated = Column(Integer, default=1, nullable=False)  # 1 = True, 0 = False
    
    created_at = Column(String(32), default=utc_now)

    # Relationships
    job = relationship("GenerationJob", back_populates="qa_reports")
    character = relationship("Character", back_populates="qa_reports")
