import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc).isoformat()

class Character(Base):
    __tablename__ = "characters"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    character_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    physical_traits = Column(Text, default="{}")  # JSON string
    gender = Column(String(30), nullable=True)
    age_range = Column(String(30), nullable=True)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(String(32), default=utc_now)
    updated_at = Column(String(32), default=utc_now, onupdate=utc_now)

    # Relationships
    assets = relationship("CharacterAsset", back_populates="character", cascade="all, delete-orphan")
    jobs = relationship("GenerationJob", back_populates="character")
    qa_reports = relationship("QAReport", back_populates="character")
    pipeline_runs = relationship("PipelineRun", back_populates="character")
