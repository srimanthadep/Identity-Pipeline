from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import PipelineRun, GenerationJob

def create_pipeline_run(db: Session, run: PipelineRun) -> PipelineRun:
    db.add(run)
    db.commit()
    db.refresh(run)
    return run

def get_pipeline_run(db: Session, pipeline_id: str) -> Optional[PipelineRun]:
    return db.query(PipelineRun).filter(PipelineRun.id == pipeline_id).first()

def list_pipeline_runs(db: Session, limit: int = 50) -> List[PipelineRun]:
    return db.query(PipelineRun).order_by(PipelineRun.created_at.desc()).limit(limit).all()

def update_pipeline_run(
    db: Session,
    run: PipelineRun,
    status: Optional[str] = None,
    completed_scenes: Optional[int] = None
) -> PipelineRun:
    if status is not None:
        run.status = status
    if completed_scenes is not None:
        run.completed_scenes = completed_scenes
    db.commit()
    db.refresh(run)
    return run

def get_pipeline_jobs(db: Session, pipeline_id: str) -> List[GenerationJob]:
    return (
        db.query(GenerationJob)
        .filter(GenerationJob.pipeline_run_id == pipeline_id)
        .order_by(GenerationJob.scene_number.asc())
        .all()
    )
