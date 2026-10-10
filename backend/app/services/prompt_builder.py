import json
from typing import Dict, Any, Tuple

class PromptBuilder:
    """
    Builds structured, identity-preserving generation prompts.
    Ensures that identity block is immutable and separated from the action/scene description.
    """

    @staticmethod
    def build_identity_block(character_name: str, gender: str, age_range: str, physical_traits: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "name": character_name,
            "gender": gender,
            "age_range": age_range,
            "traits": physical_traits
        }

    @staticmethod
    def format_identity_string(identity_block: Dict[str, Any]) -> str:
        name = identity_block.get("name", "Character")
        gender = identity_block.get("gender", "")
        age = identity_block.get("age_range", "")
        traits = identity_block.get("traits", {})
        
        trait_parts = []
        if "skin_tone" in traits:
            trait_parts.append(f"skin: {traits['skin_tone']}")
        if "hair_style" in traits:
            trait_parts.append(f"hair: {traits['hair_style']}")
        if "facial_features" in traits:
            trait_parts.append(f"features: {traits['facial_features']}")
        if "default_attire" in traits:
            trait_parts.append(f"attire: {traits['default_attire']}")
        if "distinguishing_marks" in traits:
            trait_parts.append(f"marks: {traits['distinguishing_marks']}")
            
        traits_str = ", ".join(trait_parts)
        return f"[IDENTITY: {name}, {gender}, {age}. {traits_str}]"

    @classmethod
    def assemble_prompt(cls, identity_block: Dict[str, Any], scene_prompt: str) -> str:
        id_str = cls.format_identity_string(identity_block)
        clean_scene = scene_prompt.strip()
        return f"{id_str} [SCENE: {clean_scene}]"
