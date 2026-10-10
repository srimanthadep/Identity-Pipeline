from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import GenerationJob, QAReport

def create_generation_job(db: Session, job: GenerationJob) -> GenerationJob:
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_generation_job(db: Session, job_id: str) -> Optional[GenerationJob]:
    return db.query(GenerationJob).filter(GenerationJob.id == job_id).first()

def get_character_generation_jobs(db: Session, character_id: str) -> List[GenerationJob]:
    return (
        db.query(GenerationJob)
        .filter(GenerationJob.character_id == character_id)
        .order_by(GenerationJob.created_at.desc())
        .all()
    )

def get_job_qa_reports(db: Session, job_id: str) -> List[QAReport]:
    return db.query(QAReport).filter(QAReport.job_id == job_id).all()

def update_job_status(
    db: Session,
    job: GenerationJob,
    status: str,
    output_uri: Optional[str] = None
) -> GenerationJob:
    job.status = status
    if output_uri is not None:
        job.output_uri = output_uri
    db.commit()
    db.refresh(job)
    return job
