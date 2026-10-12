import json
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.models import PipelineRun, GenerationJob
from app.crud import characters as crud_characters
from app.crud import generations as crud_generations
from app.crud import pipelines as crud_pipelines
from app.services.prompt_builder import PromptBuilder
from app.services.gemini_planner import GeminiBlueprintPlanner
from app.services.generation_service import GenerationService
from app.schemas.blueprint import (
    VideoBlueprintPlan,
    CharacterContext,
    PipelinePlanResponse,
    PipelineSceneResult,
    PipelineRunRead,
)

logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    """
    Orchestrates the end-to-end multi-scene avatar video generation pipeline:
    1. Avatar selection -> immutable CharacterContext with pinned versions
    2. Video blueprint planning -> Gemini 3.8 Flash structured output
    3. Multi-scene generation -> One Wan I2V job per scene, all sharing pinned identity anchors
    4. Per-scene QA verification and aggregation
    """

    @classmethod
    def resolve_character_context(cls, db: Session, character_identifier: str) -> CharacterContext:
        """
        Creates an immutable snapshot of character identity at avatar selection time.
        Pinned versions are locked here and reused across all scenes.
        """
        char = crud_characters.get_character_by_id_or_slug(db, character_identifier)
        if not char:
            raise ValueError(f"Character '{character_identifier}' not found.")

        canonical_asset = crud_characters.get_canonical_portrait_asset(db, char.id)
        if not canonical_asset:
            raise ValueError(f"No canonical portrait asset registered for character '{char.character_id}'.")

        traits = {}
        if char.physical_traits:
            try:
                traits = json.loads(char.physical_traits) if isinstance(char.physical_traits, str) else char.physical_traits
            except Exception:
                traits = {}

        identity_block = PromptBuilder.build_identity_block(
            character_name=char.name,
            gender=char.gender or "Character",
            age_range=char.age_range or "Adult",
            physical_traits=traits
        )
        identity_prompt = PromptBuilder.format_identity_string(identity_block)

        return CharacterContext(
            character_id=char.character_id,
            character_version=char.version,
            name=char.name,
            gender=char.gender or "Character",
            age_range=char.age_range or "Adult",
            physical_traits=traits,
            canonical_portrait_uri=canonical_asset.storage_uri,
            reference_asset_version=canonical_asset.version,
            identity_prompt=identity_prompt
        )

    @classmethod
    def create_plan(
        cls,
        db: Session,
        character_identifier: str,
        user_prompt: str
    ) -> PipelinePlanResponse:
        """
        Plans a multi-scene video blueprint using Gemini 3.8 Flash and registers a PipelineRun.
        """
        char = crud_characters.get_character_by_id_or_slug(db, character_identifier)
        if not char:
            raise ValueError(f"Character '{character_identifier}' not found.")

        # 1. Resolve frozen CharacterContext
        char_context = cls.resolve_character_context(db, character_identifier)

        # 2. Plan video blueprint via Gemini 3.8 Flash
        blueprint = GeminiBlueprintPlanner.plan_blueprint(user_prompt, char_context)

        # 3. Create persistent PipelineRun
        run = PipelineRun(
            character_id=char.id,
            character_version=char_context.character_version,
            user_prompt=user_prompt.strip(),
            blueprint_json=blueprint.model_dump_json(),
            total_scenes=blueprint.total_scenes,
            completed_scenes=0,
            status="PLANNED"
        )
        saved_run = crud_pipelines.create_pipeline_run(db, run)

        return PipelinePlanResponse(
            pipeline_id=saved_run.id,
            blueprint=blueprint,
            status=saved_run.status,
            character=char_context
        )

    @classmethod
    def execute_pipeline(
        cls,
        db: Session,
        pipeline_id: str,
        adapter_type: str = "simulated",
        seed: Optional[int] = None,
        max_retries: int = 3,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes all scenes in a planned blueprint sequentially:
        - Pins character_version and reference_asset_version across all scenes
        - Builds scene prompts incorporating camera angle instructions
        - Generates video clip and runs QA for each scene
        """
        run = crud_pipelines.get_pipeline_run(db, pipeline_id)
        if not run:
            raise ValueError(f"Pipeline run '{pipeline_id}' not found.")

        if run.status == "EXECUTING":
            raise ValueError(f"Pipeline run '{pipeline_id}' is already executing.")

        char = crud_characters.get_character_by_id_or_slug(db, run.character_id)
        canonical_asset = crud_characters.get_canonical_portrait_asset(db, char.id)

        blueprint_data = json.loads(run.blueprint_json)
        blueprint = VideoBlueprintPlan(**blueprint_data)

        # Build identity block
        traits = {}
        if char.physical_traits:
            try:
                traits = json.loads(char.physical_traits) if isinstance(char.physical_traits, str) else char.physical_traits
            except Exception:
                traits = {}

        identity_block = PromptBuilder.build_identity_block(
            character_name=char.name,
            gender=char.gender or "",
            age_range=char.age_range or "",
            physical_traits=traits
        )

        crud_pipelines.update_pipeline_run(db, run, status="EXECUTING")

        completed_count = 0
        all_passed = True

        for scene in blueprint.scenes:
            # 1. Build camera-angle aware scene prompt
            angle_val = scene.camera_angle.value if hasattr(scene.camera_angle, "value") else str(scene.camera_angle)
            shot_val = scene.shot_type.value if hasattr(scene.shot_type, "value") else str(scene.shot_type)
            
            augmented_prompt = PromptBuilder.assemble_prompt_with_angle(
                identity_block=identity_block,
                scene_prompt=scene.visual_description,
                camera_angle=angle_val
            )

            # Scene-level blueprint dictionary
            scene_blueprint = {
                "character_id": char.character_id,
                "scene_number": scene.scene_number,
                "scene_title": scene.scene_title,
                "camera_angle": angle_val,
                "shot_type": shot_val,
                "identity_block": identity_block,
                "scene_block": {
                    "raw_prompt": scene.visual_description,
                    "augmented_prompt": augmented_prompt
                },
                "generation_params": {
                    "prompt": augmented_prompt,
                    "image_url": canonical_asset.storage_uri,
                    "num_frames": 81,
                    "frames_per_second": 16,
                    "resolution": "720p",
                    "enable_prompt_expansion": False,
                    "seed": seed
                }
            }

            is_sim = 0 if adapter_type == "wan_i2v" else 1

            # 2. Persist scene GenerationJob with shared pinned versions
            job = GenerationJob(
                character_id=char.id,
                character_version=run.character_version,           # Shared PINNED version
                reference_asset_id=canonical_asset.id,
                reference_asset_version=canonical_asset.version,   # Shared PINNED version
                reference_asset_uri=canonical_asset.storage_uri,   # Shared PINNED URI
                scene_prompt=augmented_prompt,
                identity_block=json.dumps(identity_block),
                video_blueprint=json.dumps(scene_blueprint),
                adapter_type=adapter_type,
                status="PENDING",
                retry_count=0,
                max_retries=max_retries,
                adapter_config=json.dumps(custom_params or {}),
                seed=seed,
                is_simulated=is_sim,
                pipeline_run_id=run.id,
                scene_number=scene.scene_number,
                camera_angle=angle_val
            )
            saved_job = crud_generations.create_generation_job(db, job)

            # 3. Execute generation and QA
            executed = GenerationService.execute_job(db, saved_job.id)
            if executed.get("status") == "COMPLETED":
                completed_count += 1
            else:
                all_passed = False

            crud_pipelines.update_pipeline_run(db, run, completed_scenes=completed_count)

        final_status = "COMPLETED" if all_passed else "FAILED"
        crud_pipelines.update_pipeline_run(db, run, status=final_status, completed_scenes=completed_count)

        return cls.get_pipeline_status(db, run.id)

    @classmethod
    def get_pipeline_status(cls, db: Session, pipeline_id: str) -> Dict[str, Any]:
        """
        Returns complete status of a pipeline run with all decomposed scenes,
        generation jobs, video outputs, and QA scores.
        """
        run = crud_pipelines.get_pipeline_run(db, pipeline_id)
        if not run:
            raise ValueError(f"Pipeline run '{pipeline_id}' not found.")

        blueprint_data = json.loads(run.blueprint_json)
        blueprint = VideoBlueprintPlan(**blueprint_data)
        jobs = crud_pipelines.get_pipeline_jobs(db, run.id)
        job_by_scene = {j.scene_number: j for j in jobs}

        scene_results: List[Dict[str, Any]] = []
        for s in blueprint.scenes:
            job = job_by_scene.get(s.scene_number)
            job_id = job.id if job else None
            status = job.status if job else "PENDING"
            output_uri = job.output_uri if job else None
            output_url = None
            if output_uri:
                if output_uri.startswith("http://") or output_uri.startswith("https://"):
                    output_url = output_uri
                else:
                    clean_path = output_uri.replace("outputs/", "").replace("\\", "/")
                    output_url = f"/outputs/{clean_path}"

            qa_decision = None
            identity_score = None
            if job and job.qa_reports:
                latest_qa = job.qa_reports[-1]
                qa_decision = latest_qa.decision
                identity_score = latest_qa.identity_score

            is_sim = bool(job.is_simulated) if job else True

            scene_results.append({
                "scene_number": s.scene_number,
                "scene_title": s.scene_title,
                "camera_angle": s.camera_angle.value if hasattr(s.camera_angle, "value") else str(s.camera_angle),
                "shot_type": s.shot_type.value if hasattr(s.shot_type, "value") else str(s.shot_type),
                "visual_description": s.visual_description,
                "character_action": s.character_action,
                "environment": s.environment,
                "job_id": job_id,
                "status": status,
                "output_uri": output_uri,
                "output_url": output_url,
                "qa_decision": qa_decision,
                "identity_score": identity_score,
                "is_simulated": is_sim
            })

        return {
            "id": run.id,
            "character_id": run.character.character_id if run.character else run.character_id,
            "character_name": run.character.name if run.character else "",
            "character_version": run.character_version,
            "user_prompt": run.user_prompt,
            "blueprint": blueprint.model_dump(),
            "total_scenes": run.total_scenes,
            "completed_scenes": run.completed_scenes,
            "status": run.status,
            "created_at": run.created_at,
            "updated_at": run.updated_at,
            "scenes": scene_results
        }
