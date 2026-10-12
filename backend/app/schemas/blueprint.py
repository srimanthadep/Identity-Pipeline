from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class CameraAngle(str, Enum):
    FRONT = "front"
    THREE_QUARTER = "three_quarter"
    SIDE_PROFILE = "side_profile"
    OVER_SHOULDER = "over_shoulder"
    WIDE = "wide"
    CLOSE_UP = "close_up"

class ShotType(str, Enum):
    ESTABLISHING = "establishing"
    MEDIUM = "medium"
    CLOSE_UP = "close_up"
    EXTREME_CLOSE_UP = "extreme_close_up"
    FULL_BODY = "full_body"
    OVER_THE_SHOULDER = "over_the_shoulder"

class ScenePlan(BaseModel):
    """A single scene in the video blueprint."""
    scene_number: int = Field(description="Sequential scene number starting from 1")
    scene_title: str = Field(description="Short descriptive title for the scene")
    visual_description: str = Field(
        description="Detailed visual prompt for Wan I2V generation. "
        "Describe what is visually happening, DO NOT include character physical "
        "description (that is injected separately via identity block)."
    )
    camera_angle: CameraAngle = Field(
        description="Primary camera angle for this scene"
    )
    shot_type: ShotType = Field(
        description="The shot framing type"
    )
    character_action: str = Field(
        description="What the character is physically doing in this scene"
    )
    environment: str = Field(
        description="Background/setting description for the scene"
    )
    estimated_duration_seconds: float = Field(
        default=5.0,
        description="Target duration for this clip (max 5s per Wan I2V clip)"
    )
    transition_from_previous: Optional[str] = Field(
        default=None,
        description="How this scene connects to the previous one visually"
    )

class VideoBlueprintPlan(BaseModel):
    """Complete video blueprint decomposed by Gemini."""
    title: str = Field(description="Title for the complete video")
    total_scenes: int = Field(description="Total number of scenes in the blueprint")
    character_id: str = Field(description="The predefined avatar identifier used")
    scenes: List[ScenePlan] = Field(description="List of scenes in chronological order")
    narrative_summary: str = Field(
        description="1-2 sentence summary of the complete video narrative"
    )

class CharacterContext(BaseModel):
    """Immutable snapshot of a character at selection time."""
    character_id: str
    character_version: int
    name: str
    gender: str
    age_range: str
    physical_traits: Dict[str, Any]
    canonical_portrait_uri: str
    reference_asset_version: int
    identity_prompt: str

class PipelinePlanRequest(BaseModel):
    character_id: str = Field(..., description="Target character UUID or slug (e.g. char_01_priya)")
    user_prompt: str = Field(..., description="High-level narrative video prompt from the user")

class PipelinePlanResponse(BaseModel):
    pipeline_id: str
    blueprint: VideoBlueprintPlan
    status: str
    character: CharacterContext

class PipelineExecuteRequest(BaseModel):
    adapter_type: Optional[str] = Field("simulated", description="'simulated' or 'wan_i2v'")
    seed: Optional[int] = None
    max_retries: Optional[int] = 3
    custom_params: Optional[Dict[str, Any]] = None

class PipelineSceneResult(BaseModel):
    scene_number: int
    scene_title: str
    camera_angle: str
    shot_type: str
    job_id: Optional[str] = None
    status: str
    output_uri: Optional[str] = None
    output_url: Optional[str] = None
    qa_decision: Optional[str] = None
    identity_score: Optional[float] = None
    is_simulated: Optional[bool] = None

class PipelineRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    character_id: str
    character_version: int
    user_prompt: str
    blueprint: VideoBlueprintPlan
    total_scenes: int
    completed_scenes: int
    status: str
    created_at: str
    updated_at: str
    scenes: List[PipelineSceneResult] = []
