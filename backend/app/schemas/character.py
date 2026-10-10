from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class CharacterAssetBase(BaseModel):
    asset_type: str = Field(..., description="Asset type: e.g. portrait, sheet_front")
    storage_uri: str = Field(..., description="URI or path to the asset")
    mime_type: Optional[str] = "image/png"
    is_canonical: bool = True
    version: int = 1

class CharacterAssetRead(CharacterAssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    character_id: str
    created_at: str

class CharacterBase(BaseModel):
    character_id: str = Field(..., description="Unique slug like char_01_priya")
    name: str = Field(..., description="Character display name")
    description: Optional[str] = None
    physical_traits: Dict[str, Any] = Field(default_factory=dict)
    gender: Optional[str] = None
    age_range: Optional[str] = None

class CharacterCreate(CharacterBase):
    version: int = 1

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    physical_traits: Optional[Dict[str, Any]] = None
    gender: Optional[str] = None
    age_range: Optional[str] = None

class CharacterRead(CharacterBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    version: int
    created_at: str
    updated_at: str
    canonical_portrait_url: Optional[str] = None

class CharacterDetailRead(CharacterRead):
    assets: List[CharacterAssetRead] = []
