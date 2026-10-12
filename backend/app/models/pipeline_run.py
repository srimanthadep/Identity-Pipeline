import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc).isoformat()

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    character_id = Column(String(36), ForeignKey("characters.id"), nullable=False, index=True)
    character_version = Column(Integer, nullable=False)
    user_prompt = Column(Text, nullable=False)
    blueprint_json = Column(Text, nullable=False)
    total_scenes = Column(Integer, nullable=False)
    completed_scenes = Column(Integer, default=0, nullable=False)
    status = Column(String(30), default="PLANNED", nullable=False, index=True)  # PLANNED, EXECUTING, COMPLETED, FAILED
    
    created_at = Column(String(32), default=utc_now)
    updated_at = Column(String(32), default=utc_now, onupdate=utc_now)

    # Relationships
    character = relationship("Character", back_populates="pipeline_runs")
    jobs = relationship("GenerationJob", back_populates="pipeline_run", cascade="all, delete-orphan", order_by="GenerationJob.scene_number")
