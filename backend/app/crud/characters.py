from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import Character, CharacterAsset

def get_characters(db: Session, skip: int = 0, limit: int = 100) -> List[Character]:
    return db.query(Character).offset(skip).limit(limit).all()

def get_character_by_id_or_slug(db: Session, identifier: str) -> Optional[Character]:
    # Match either UUID id or character_id slug
    return db.query(Character).filter(
        (Character.id == identifier) | (Character.character_id == identifier)
    ).first()

def get_character_assets(db: Session, character_id: str) -> List[CharacterAsset]:
    return db.query(CharacterAsset).filter(CharacterAsset.character_id == character_id).all()

def get_canonical_portrait_asset(db: Session, character_id: str) -> Optional[CharacterAsset]:
    return db.query(CharacterAsset).filter(
        CharacterAsset.character_id == character_id,
        CharacterAsset.asset_type == "portrait",
        CharacterAsset.is_canonical == 1
    ).first()

def update_character(db: Session, character: Character, updates: Dict[str, Any]) -> Character:
    for key, val in updates.items():
        if val is not None and hasattr(character, key):
            setattr(character, key, val)
    # Increment version when character metadata is modified
    character.version += 1
    db.commit()
    db.refresh(character)
    return character
