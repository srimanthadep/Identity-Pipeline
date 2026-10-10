from typing import Dict, Any, Optional
from app.services.prompt_builder import PromptBuilder

class BlueprintGenerator:
    """
    Constructs the canonical VideoBlueprint specification.
    Includes verified Fal.ai Wan 2.2 schema parameters with enable_prompt_expansion: false.
    """

    @classmethod
    def generate_blueprint(
        cls,
        character_id: str,
        character_name: str,
        gender: str,
        age_range: str,
        physical_traits: Dict[str, Any],
        scene_prompt: str,
        reference_image_uri: str,
        seed: Optional[int] = None,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        identity_block = PromptBuilder.build_identity_block(
            character_name=character_name,
            gender=gender,
            age_range=age_range,
            physical_traits=physical_traits
        )
        augmented_prompt = PromptBuilder.assemble_prompt(identity_block, scene_prompt)

        # Verified official Fal.ai Wan 2.2-A14B defaults from official schema
        generation_params = {
            "prompt": augmented_prompt,
            "image_url": reference_image_uri,
            "num_frames": 81,               # 81 frames default (~5 sec at 16fps)
            "frames_per_second": 16,        # 16 fps default
            "resolution": "720p",           # 720p official default
            "aspect_ratio": "auto",
            "num_inference_steps": 27,      # 27 steps official default
            "guidance_scale": 3.5,          # 3.5 official default
            "guidance_scale_2": 3.5,
            "shift": 5.0,
            "enable_prompt_expansion": False, # CRITICAL: MUST BE FALSE FOR IDENTITY FIDELITY
            "acceleration": "regular",
            "interpolator_model": "film",
            "num_interpolated_frames": 1,
            "video_quality": "high",
            "video_write_mode": "balanced",
            "negative_prompt": "face distortion, morphed face, extra limbs, ugly, blurred features, identity change",
            "seed": seed
        }

        if custom_params:
            for k, v in custom_params.items():
                if k != "enable_prompt_expansion": # Protect this parameter
                    generation_params[k] = v

        return {
            "character_id": character_id,
            "identity_block": identity_block,
            "scene_block": {
                "raw_prompt": scene_prompt,
                "augmented_prompt": augmented_prompt
            },
            "generation_params": generation_params
        }
