import os
import json
import logging
from typing import Optional
from app.config import settings
from app.schemas.blueprint import (
    CameraAngle,
    ShotType,
    ScenePlan,
    VideoBlueprintPlan,
    CharacterContext,
)

logger = logging.getLogger(__name__)

BLUEPRINT_SYSTEM_PROMPT = """
You are a professional video director and scene planner for an AI video generation pipeline.

Your job is to take a user's free-form video prompt and decompose it into discrete, 
filmable scenes. Each scene will be independently rendered as a 5-second video clip 
using an Image-to-Video AI model (Wan 2.2).

RULES:
1. Each scene should be at most ~5 seconds of action (this is the I2V model's max clip length).
2. DO NOT describe the character's physical appearance in visual_description — 
   the character's identity block (physical traits, attire, etc.) is injected 
   separately and automatically by the pipeline.
3. DO describe what the character is DOING, the environment, lighting, mood, 
   and camera movement.
4. Choose camera_angle and shot_type that best serve the storytelling.
5. ANGLE PREFERENCE (when narratively appropriate):
   - PREFER front or three_quarter angles — these produce the highest 
     identity fidelity with the front-facing reference portrait.
   - Use side_profile or over_shoulder ONLY when the story requires it.
   - NEVER use back-view-only scenes unless absolutely necessary for narrative.
6. Keep scenes visually distinct but narratively connected.
7. Limit total scenes to 3-6 for a single video prompt.

CHARACTER CONTEXT (provided by the system, DO NOT modify):
{character_context}
"""

class GeminiBlueprintPlanner:
    """
    Decomposes free-form user video prompts into structured multi-scene blueprints
    using Gemini 3.8 Flash with deterministic JSON schema output.
    Provides intelligent simulated fallback when API key is not configured or offline.
    """

    @classmethod
    def plan_blueprint(
        cls,
        user_prompt: str,
        character_context: CharacterContext
    ) -> VideoBlueprintPlan:
        api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        model_name = settings.GEMINI_MODEL or "gemini-3.8-flash"

        if api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)

                system_prompt = BLUEPRINT_SYSTEM_PROMPT.format(
                    character_context=character_context.model_dump_json(indent=2)
                )

                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        system_prompt,
                        f"Plan a video blueprint for this prompt:\n\n{user_prompt}"
                    ],
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": VideoBlueprintPlan,
                        "temperature": 0.3,
                    },
                )

                if hasattr(response, "parsed") and response.parsed:
                    blueprint = response.parsed
                    if isinstance(blueprint, VideoBlueprintPlan):
                        blueprint.character_id = character_context.character_id
                        return blueprint
                
                # If parsed is a dict or string
                text_content = response.text
                data = json.loads(text_content)
                data["character_id"] = character_context.character_id
                return VideoBlueprintPlan(**data)

            except Exception as e:
                logger.warning(
                    f"Gemini API call failed or unavailable ({e}). "
                    "Falling back to simulated blueprint planner."
                )

        logger.info("Using simulated fallback blueprint generator (GEMINI_API_KEY not configured or call failed).")
        return cls._generate_fallback_blueprint(user_prompt, character_context)

    @classmethod
    def _generate_fallback_blueprint(
        cls,
        user_prompt: str,
        character_context: CharacterContext
    ) -> VideoBlueprintPlan:
        """
        Deterministic, context-aware fallback blueprint generator that decomposes
        the user prompt into coherent cinematic scenes matching the character context.
        """
        name = character_context.name
        char_id = character_context.character_id
        clean_prompt = user_prompt.strip()

        # Parse sentences or clauses
        parts = [p.strip() for p in clean_prompt.replace(" then ", ", ").replace(" and ", ", ").split(",") if p.strip()]
        if len(parts) < 3:
            parts = [
                f"{name} arrives at the location and looks around attentively",
                f"{name} engages with the central object or activity in the setting",
                f"{name} pauses, reflects, and smiles with a confident demeanor",
                f"{name} moves forward into the scene with purposeful momentum"
            ]

        scenes = [
            ScenePlan(
                scene_number=1,
                scene_title="Arrival & Establishing Shot",
                visual_description=f"A wide view establishing the scene environment as {name} enters smoothly. Sunlight and atmospheric depth highlight the setting as {name} surveys the surroundings.",
                camera_angle=CameraAngle.WIDE,
                shot_type=ShotType.ESTABLISHING,
                character_action=f"Entering the setting, observing the surroundings with keen interest",
                environment="Atmospheric Indian locale with authentic architectural and cultural ambiance",
                estimated_duration_seconds=5.0,
                transition_from_previous=None
            ),
            ScenePlan(
                scene_number=2,
                scene_title="Engagement & Interaction",
                visual_description=f"{name} steps closer to interact with the environment, hands in motion. Warm natural lighting illuminates the immediate surroundings.",
                camera_angle=CameraAngle.THREE_QUARTER,
                shot_type=ShotType.MEDIUM,
                character_action=f"Engaging with the main activity: {parts[0] if parts else 'inspecting details'}",
                environment="Detailed foreground setting with rich textures and natural lighting",
                estimated_duration_seconds=5.0,
                transition_from_previous="Cut to medium three-quarter framing following movement"
            ),
            ScenePlan(
                scene_number=3,
                scene_title="Character Focus & Emotion",
                visual_description=f"Direct close-up view of {name} looking toward the camera focal plane, expression shifting to genuine warmth and subtle confidence.",
                camera_angle=CameraAngle.FRONT,
                shot_type=ShotType.CLOSE_UP,
                character_action=f"Reflective expression, gentle smile, looking directly ahead",
                environment="Softly blurred background emphasizing character emotional presence",
                estimated_duration_seconds=5.0,
                transition_from_previous="Smooth cut into intimate front-facing portrait angle"
            ),
            ScenePlan(
                scene_number=4,
                scene_title="Resolution & Continuation",
                visual_description=f"{name} completes the interaction and turns gracefully, taking a confident step forward toward their next objective as the scene resolves.",
                camera_angle=CameraAngle.THREE_QUARTER,
                shot_type=ShotType.MEDIUM,
                character_action=f"Concluding the sequence and walking forward with graceful confidence",
                environment="Wide ambient lighting, bustling depth in the background",
                estimated_duration_seconds=5.0,
                transition_from_previous="Cut to three-quarter tracking shot resolving the moment"
            )
        ]

        title = f"{name}'s Journey — {clean_prompt[:30].strip()}..." if len(clean_prompt) > 30 else f"{name}'s Sequence"

        return VideoBlueprintPlan(
            title=title,
            total_scenes=len(scenes),
            character_id=char_id,
            scenes=scenes,
            narrative_summary=f"{name} steps into the scene, engages with the focal elements, shares an expressive moment, and smoothly transitions forward."
        )
