from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.qa import QAReportRead

class VideoBlueprintSchema(BaseModel):
    character_id: str
    identity_block: Dict[str, Any]
    scene_block: Dict[str, Any]
    generation_params: Dict[str, Any]

class GenerationJobCreate(BaseModel):
    character_id: str = Field(..., description="Target character UUID or character_id slug")
    scene_prompt: str = Field(..., description="Action/scene prompt")
    adapter_type: Optional[str] = Field("simulated", description="'simulated' or 'wan_i2v'")
    seed: Optional[int] = None
    max_retries: Optional[int] = 3
    adapter_config: Optional[Dict[str, Any]] = Field(default_factory=dict)

class GenerationRetryRequest(BaseModel):
    reason: Optional[str] = "Manual retry request"

class GenerationJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    character_id: str
    character_version: int
    reference_asset_id: str
    reference_asset_version: int
    reference_asset_uri: str
    scene_prompt: str
    identity_block: Dict[str, Any]
    video_blueprint: Dict[str, Any]
    adapter_type: str
    status: str
    output_uri: Optional[str] = None
    retry_count: int
    max_retries: int
    adapter_config: Dict[str, Any]
    seed: Optional[int] = None
    is_simulated: bool
    created_at: str
    updated_at: str
    qa_reports: List[QAReportRead] = []
