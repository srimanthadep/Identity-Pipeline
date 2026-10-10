import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.crud import characters as crud_characters
from app.schemas.character import CharacterRead, CharacterDetailRead, CharacterAssetRead

class CharacterService:
    @staticmethod
    def _format_character(char, canonical_asset=None) -> Dict[str, Any]:
        traits = {}
        if char.physical_traits:
            try:
                traits = json.loads(char.physical_traits) if isinstance(char.physical_traits, str) else char.physical_traits
            except Exception:
                traits = {}
                
        portrait_url = None
        if canonical_asset:
            portrait_url = f"/assets/{canonical_asset.storage_uri}"
            
        return {
            "id": char.id,
            "character_id": char.character_id,
            "name": char.name,
            "description": char.description,
            "physical_traits": traits,
            "gender": char.gender,
            "age_range": char.age_range,
            "version": char.version,
            "created_at": char.created_at,
            "updated_at": char.updated_at,
            "canonical_portrait_url": portrait_url
        }

    @classmethod
    def list_characters(cls, db: Session) -> List[Dict[str, Any]]:
        chars = crud_characters.get_characters(db)
        results = []
        for c in chars:
            canonical = crud_characters.get_canonical_portrait_asset(db, c.id)
            results.append(cls._format_character(c, canonical))
        return results

    @classmethod
    def get_character_detail(cls, db: Session, identifier: str) -> Optional[Dict[str, Any]]:
        c = crud_characters.get_character_by_id_or_slug(db, identifier)
        if not c:
            return None
        assets = crud_characters.get_character_assets(db, c.id)
        canonical = next((a for a in assets if a.is_canonical and a.asset_type == "portrait"), None)
        formatted = cls._format_character(c, canonical)
        formatted["assets"] = [
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
        return formatted
