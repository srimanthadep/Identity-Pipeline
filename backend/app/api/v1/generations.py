from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.schemas.generation import GenerationJobCreate, GenerationRetryRequest
from app.services.generation_service import GenerationService
from app.crud import generations as crud_generations
from app.crud import characters as crud_characters

router = APIRouter(prefix="/generations", tags=["Generations"])

def _bg_execute(job_id: str):
    db = SessionLocal()
    try:
        GenerationService.execute_job(db, job_id)
    finally:
        db.close()

@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_generation(
    payload: GenerationJobCreate,
    background_tasks: BackgroundTasks,
    run_sync: bool = False,
    db: Session = Depends(get_db)
):
    """
    Create a new video generation job for a character.
    Pins current character_version and reference_asset_version.
    """
    try:
        job_data = GenerationService.create_generation_job(
            db=db,
            character_identifier=payload.character_id,
            scene_prompt=payload.scene_prompt,
            adapter_type=payload.adapter_type or "simulated",
            seed=payload.seed,
            max_retries=payload.max_retries or 3,
            adapter_config=payload.adapter_config
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    job_id = job_data["id"]

    if run_sync:
        # Run synchronously (useful for tests or immediate demo needs)
        job_data = GenerationService.execute_job(db, job_id)
    else:
        # Run in background task
        background_tasks.add_task(_bg_execute, job_id)

    return job_data

@router.get("/{job_id}", response_model=Dict[str, Any])
def get_generation(job_id: str, db: Session = Depends(get_db)):
    """Retrieve generation job status, pinned versions, output, and is_simulated flag."""
    job = crud_generations.get_generation_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation job '{job_id}' not found."
        )
    return GenerationService._format_job(job)

@router.get("/{job_id}/qa", response_model=List[Dict[str, Any]])
def get_generation_qa(job_id: str, db: Session = Depends(get_db)):
    """Retrieve QA evaluation reports for a generation job."""
    job = crud_generations.get_generation_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation job '{job_id}' not found."
        )
    formatted = GenerationService._format_job(job)
    return formatted.get("qa_reports", [])

@router.post("/{job_id}/retry", response_model=Dict[str, Any])
def retry_generation(
    job_id: str,
    payload: Optional[GenerationRetryRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Retry a generation job using the EXACT original pinned character_version
    and reference_asset_version.
    """
    try:
        updated_job = GenerationService.retry_job(db, job_id)
        return updated_job
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/by-character/{character_id}", response_model=List[Dict[str, Any]])
def get_character_generations(character_id: str, db: Session = Depends(get_db)):
    """Retrieve all generation history for a specific character."""
    char = crud_characters.get_character_by_id_or_slug(db, character_id)
    if not char:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found."
        )
    jobs = crud_generations.get_character_generation_jobs(db, char.id)
    return [GenerationService._format_job(j) for j in jobs]
