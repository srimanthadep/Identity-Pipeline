from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.character_service import CharacterService
from app.crud import characters as crud_characters

router = APIRouter(prefix="/characters", tags=["Characters"])

@router.get("", response_model=List[Dict[str, Any]])
def list_characters(db: Session = Depends(get_db)):
    """Retrieve all 10 avatars in the library with their canonical portraits."""
    return CharacterService.list_characters(db)

@router.get("/{character_id}", response_model=Dict[str, Any])
def get_character(character_id: str, db: Session = Depends(get_db)):
    """Retrieve character profile by UUID or slug (e.g. char_01_priya)."""
    character = CharacterService.get_character_detail(db, character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found."
        )
    return character

@router.get("/{character_id}/assets", response_model=List[Dict[str, Any]])
def get_character_assets(character_id: str, db: Session = Depends(get_db)):
    """Retrieve all registered assets for a character."""
    character = crud_characters.get_character_by_id_or_slug(db, character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found."
        )
    assets = crud_characters.get_character_assets(db, character.id)
    return [
        {
            "id": a.id,
            "character_id": a.character_id,
            "asset_type": a.asset_type,
            "storage_uri": a.storage_uri,
            "mime_type": a.mime_type,
            "is_canonical": bool(a.is_canonical),
            "version": a.version,
            "created_at": a.created_at,
            "url": f"/assets/{a.storage_uri}"
        }
        for a in assets
    ]
