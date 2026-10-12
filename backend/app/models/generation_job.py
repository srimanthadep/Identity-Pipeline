import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc).isoformat()

class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    character_id = Column(String(36), ForeignKey("characters.id"), nullable=False, index=True)
    character_version = Column(Integer, nullable=False)  # PINNED at creation
    reference_asset_id = Column(String(36), ForeignKey("character_assets.id"), nullable=False)
    reference_asset_version = Column(Integer, nullable=False)  # PINNED at creation
    reference_asset_uri = Column(String(500), nullable=False)  # SNAPSHOT at creation
    
    scene_prompt = Column(Text, nullable=False)
    identity_block = Column(Text, nullable=False)  # JSON string
    video_blueprint = Column(Text, nullable=False)  # JSON string
    
    adapter_type = Column(String(50), default="simulated", nullable=False)
    status = Column(String(30), default="PENDING", nullable=False, index=True)  # PENDING, RUNNING, COMPLETED, FAILED
    output_uri = Column(String(500), nullable=True)
    
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    adapter_config = Column(Text, default="{}")  # JSON string
    seed = Column(Integer, nullable=True)
    is_simulated = Column(Integer, default=1, nullable=False)  # 1 = True, 0 = False

    # Pipeline linkage
    pipeline_run_id = Column(String(36), ForeignKey("pipeline_runs.id"), nullable=True, index=True)
    scene_number = Column(Integer, nullable=True)
    camera_angle = Column(String(50), nullable=True)
    
    created_at = Column(String(32), default=utc_now)
    updated_at = Column(String(32), default=utc_now, onupdate=utc_now)

    # Relationships
    character = relationship("Character", back_populates="jobs")
    reference_asset = relationship("CharacterAsset", back_populates="jobs")
    pipeline_run = relationship("PipelineRun", back_populates="jobs")
    qa_reports = relationship("QAReport", back_populates="job", cascade="all, delete-orphan")
