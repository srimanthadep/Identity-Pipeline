import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models import GenerationJob, Character, CharacterAsset
from app.crud import characters as crud_characters
from app.crud import generations as crud_generations
from app.services.blueprint_generator import BlueprintGenerator
from app.services.qa_service import QAService
from app.adapters import get_adapter
from app.config import settings

logger = logging.getLogger(__name__)

class GenerationService:
    @staticmethod
    def _format_job(job: GenerationJob) -> Dict[str, Any]:
        identity_block = {}
        blueprint = {}
        adapter_config = {}
        try:
            identity_block = json.loads(job.identity_block) if isinstance(job.identity_block, str) else job.identity_block
        except Exception:
            pass
        try:
            blueprint = json.loads(job.video_blueprint) if isinstance(job.video_blueprint, str) else job.video_blueprint
        except Exception:
            pass
        try:
            adapter_config = json.loads(job.adapter_config) if isinstance(job.adapter_config, str) else job.adapter_config
        except Exception:
            pass

        qa_reports_data = []
        for qr in (job.qa_reports or []):
            qr_metrics = {}
            try:
                qr_metrics = json.loads(qr.metrics) if isinstance(qr.metrics, str) else qr.metrics
            except Exception:
                pass
            qa_reports_data.append({
                "id": qr.id,
                "job_id": qr.job_id,
                "character_id": qr.character_id,
                "identity_score": qr.identity_score,
                "appearance_score": qr.appearance_score,
                "decision": qr.decision,
                "metrics": qr_metrics,
                "reference_asset_uri": qr.reference_asset_uri,
                "evaluated_asset_uri": qr.evaluated_asset_uri,
                "is_simulated": bool(qr.is_simulated),
                "created_at": qr.created_at
            })

        output_url = None
        if job.output_uri:
            if job.output_uri.startswith("http://") or job.output_uri.startswith("https://"):
                output_url = job.output_uri
            else:
                # Local static output
                clean_path = job.output_uri.replace("outputs/", "").replace("\\", "/")
                output_url = f"/outputs/{clean_path}"

        return {
            "id": job.id,
            "character_id": job.character_id,
            "character_version": job.character_version,
            "reference_asset_id": job.reference_asset_id,
            "reference_asset_version": job.reference_asset_version,
            "reference_asset_uri": job.reference_asset_uri,
            "scene_prompt": job.scene_prompt,
            "identity_block": identity_block,
            "video_blueprint": blueprint,
            "adapter_type": job.adapter_type,
            "status": job.status,
            "output_uri": job.output_uri,
            "output_url": output_url,
            "retry_count": job.retry_count,
            "max_retries": job.max_retries,
            "adapter_config": adapter_config,
            "seed": job.seed,
            "is_simulated": bool(job.is_simulated),
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "qa_reports": qa_reports_data
        }

    @classmethod
    def create_generation_job(
        cls,
        db: Session,
        character_identifier: str,
        scene_prompt: str,
        adapter_type: str = "simulated",
        seed: Optional[int] = None,
        max_retries: int = 3,
        adapter_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # 1. Resolve character
        char = crud_characters.get_character_by_id_or_slug(db, character_identifier)
        if not char:
            raise ValueError(f"Character '{character_identifier}' not found.")

        # 2. Resolve canonical reference asset
        canonical_asset = crud_characters.get_canonical_portrait_asset(db, char.id)
        if not canonical_asset:
            raise ValueError(f"No canonical portrait asset registered for character '{char.character_id}'.")

        # 3. PIN VERSIONS AND SNAPSHOTS
        pinned_character_version = char.version
        pinned_asset_version = canonical_asset.version
        pinned_asset_uri = canonical_asset.storage_uri

        traits = {}
        if char.physical_traits:
            try:
                traits = json.loads(char.physical_traits) if isinstance(char.physical_traits, str) else char.physical_traits
            except Exception:
                traits = {}

        # 4. Generate Video Blueprint
        blueprint = BlueprintGenerator.generate_blueprint(
            character_id=char.character_id,
            character_name=char.name,
            gender=char.gender or "",
            age_range=char.age_range or "",
            physical_traits=traits,
            scene_prompt=scene_prompt,
            reference_image_uri=pinned_asset_uri,
            seed=seed,
            custom_params=adapter_config
        )

        is_simulated = 0 if adapter_type == "wan_i2v" else 1

        # 5. Persist Job
        job = GenerationJob(
            character_id=char.id,
            character_version=pinned_character_version,
            reference_asset_id=canonical_asset.id,
            reference_asset_version=pinned_asset_version,
            reference_asset_uri=pinned_asset_uri,
            scene_prompt=scene_prompt,
            identity_block=json.dumps(blueprint["identity_block"]),
            video_blueprint=json.dumps(blueprint),
            adapter_type=adapter_type,
            status="PENDING",
            retry_count=0,
            max_retries=max_retries,
            adapter_config=json.dumps(adapter_config or {}),
            seed=seed,
            is_simulated=is_simulated
        )

        saved_job = crud_generations.create_generation_job(db, job)
        return cls._format_job(saved_job)

    @classmethod
    def execute_job(cls, db: Session, job_id: str, force_qa_score: Optional[float] = None) -> Dict[str, Any]:
        """Executes the generation job using its adapter and runs QA."""
        job = crud_generations.get_generation_job(db, job_id)
        if not job:
            raise ValueError(f"Generation job '{job_id}' not found.")

        job.status = "RUNNING"
        db.commit()

        try:
            adapter = get_adapter(job.adapter_type)
            blueprint = json.loads(job.video_blueprint)
            ref_path = settings.ASSETS_DIR / job.reference_asset_uri

            result = adapter.generate(
                job_id=job.id,
                blueprint=blueprint,
                reference_asset_path=ref_path,
                output_dir=settings.OUTPUTS_DIR
            )

            job.output_uri = result.get("output_uri")
            job.is_simulated = 1 if result.get("is_simulated", True) else 0
            job.status = "COMPLETED"
            db.commit()
            db.refresh(job)

            # Evaluate QA
            qa_report = QAService.evaluate_job(db, job, forced_score=force_qa_score)

            # Handle automatic retry if QA fails and retries remaining
            if qa_report.decision == "FAIL" and job.retry_count < job.max_retries:
                logger.info(f"Job {job.id} QA failed. Triggering auto-retry ({job.retry_count + 1}/{job.max_retries})...")
                cls.retry_job(db, job.id)

        except Exception as e:
            logger.error(f"Job {job_id} generation failed: {e}", exc_info=True)
            job.status = "FAILED"
            db.commit()

        db.refresh(job)
        return cls._format_job(job)

    @classmethod
    def retry_job(cls, db: Session, job_id: str) -> Dict[str, Any]:
        """
        Retries a generation job while STRICTLY PRESERVING pinned character_version,
        reference_asset_version, and reference_asset_uri.
        """
        job = crud_generations.get_generation_job(db, job_id)
        if not job:
            raise ValueError(f"Job '{job_id}' not found.")

        if job.retry_count >= job.max_retries:
            raise ValueError(
                f"Maximum retry limit ({job.max_retries}) reached for job '{job_id}'. "
                "Marked for human review."
            )

        job.retry_count += 1
        job.status = "PENDING"
        # Notice: character_version, reference_asset_version, and reference_asset_uri are UNCHANGED!
        db.commit()
        db.refresh(job)

        # Re-execute job with the preserved pinned versions
        return cls.execute_job(db, job.id)
