from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class QAReportBase(BaseModel):
    identity_score: Optional[float] = None
    appearance_score: Optional[float] = None
    decision: str = Field(..., description="'PASS', 'FAIL', 'REVIEW'")
    metrics: Dict[str, Any] = Field(default_factory=dict)
    reference_asset_uri: Optional[str] = None
    evaluated_asset_uri: Optional[str] = None
    is_simulated: bool = True

class QAReportCreate(QAReportBase):
    job_id: str
    character_id: str

class QAReportRead(QAReportBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_id: str
    character_id: str
    created_at: str
