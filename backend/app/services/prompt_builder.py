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

    @classmethod
    def assemble_prompt_with_angle(
        cls,
        identity_block: Dict[str, Any],
        scene_prompt: str,
        camera_angle: str = "front"
    ) -> str:
        """
        Builds the final Wan I2V prompt with camera angle guidance to steer
        orientation while anchoring the identity block.
        """
        angle_hints = {
            "front": "facing the camera directly",
            "three_quarter": "at a three-quarter angle, slightly turned",
            "side_profile": "shown from the side in profile view",
            "over_shoulder": "seen from behind and over the shoulder",
            "wide": "in a wide establishing shot",
            "close_up": "in a detailed close-up shot"
        }
        angle_key = str(camera_angle).lower().replace("cameraangle.", "")
        angle_text = angle_hints.get(angle_key, "")
        clean_scene = scene_prompt.strip()
        if angle_text and angle_text not in clean_scene.lower():
            clean_scene = f"{clean_scene}. Camera: {angle_text}."
        id_str = cls.format_identity_string(identity_block)
        return f"{id_str} [SCENE: {clean_scene}]"
