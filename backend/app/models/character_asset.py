import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc).isoformat()

class CharacterAsset(Base):
    __tablename__ = "character_assets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    character_id = Column(String(36), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False)  # 'portrait', 'sheet_front', etc.
    storage_uri = Column(String(500), nullable=False)
    mime_type = Column(String(50), default="image/png")
    is_canonical = Column(Integer, default=0, nullable=False)  # 1 for canonical, 0 otherwise
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(String(32), default=utc_now)

    # Relationships
    character = relationship("Character", back_populates="assets")
    jobs = relationship("GenerationJob", back_populates="reference_asset")
