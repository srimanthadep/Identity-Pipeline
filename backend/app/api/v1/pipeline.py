from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, Query
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.schemas.blueprint import (
    PipelinePlanRequest,
    PipelinePlanResponse,
    PipelineExecuteRequest,
    PipelineRunRead,
    PipelineSceneResult,
)
from app.services.pipeline_orchestrator import PipelineOrchestrator
from app.crud import pipelines as crud_pipelines

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])

def _bg_execute_pipeline(
    pipeline_id: str,
    adapter_type: str = "simulated",
    seed: Optional[int] = None,
    max_retries: int = 3,
    custom_params: Optional[Dict[str, Any]] = None
):
    db = SessionLocal()
    try:
        PipelineOrchestrator.execute_pipeline(
            db=db,
            pipeline_id=pipeline_id,
            adapter_type=adapter_type,
            seed=seed,
            max_retries=max_retries,
            custom_params=custom_params
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Background execution of pipeline {pipeline_id} failed: {e}", exc_info=True)
    finally:
        db.close()

@router.post("/plan", response_model=PipelinePlanResponse, status_code=status.HTTP_201_CREATED)
def plan_pipeline(payload: PipelinePlanRequest, db: Session = Depends(get_db)):
    """
    Submits user prompt + character_id -> uses Gemini 3.8 Flash to plan a multi-scene
    cinematic video blueprint with camera angles and framing.
    """
    try:
        plan_response = PipelineOrchestrator.create_plan(
            db=db,
            character_identifier=payload.character_id,
            user_prompt=payload.user_prompt
        )
        return plan_response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Planning failed: {str(e)}")

@router.post("/execute/{pipeline_id}", response_model=Dict[str, Any])
def execute_pipeline(
    pipeline_id: str,
    background_tasks: BackgroundTasks,
    payload: Optional[PipelineExecuteRequest] = None,
    run_sync: bool = False,
    db: Session = Depends(get_db)
):
    """
    Executes all scenes in a planned blueprint sequentially:
    Pins identity across all scenes, calls Wan I2V generation, and runs identity QA.
    """
    adapter_type = payload.adapter_type if payload and payload.adapter_type else "simulated"
    seed = payload.seed if payload else None
    max_retries = payload.max_retries if payload and payload.max_retries is not None else 3
    custom_params = payload.custom_params if payload else None

    # Verify pipeline exists
    run = crud_pipelines.get_pipeline_run(db, pipeline_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pipeline run '{pipeline_id}' not found.")

    if run.status == "EXECUTING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Pipeline run '{pipeline_id}' is already executing.")

    if run_sync:
        result = PipelineOrchestrator.execute_pipeline(
            db=db,
            pipeline_id=pipeline_id,
            adapter_type=adapter_type,
            seed=seed,
            max_retries=max_retries,
            custom_params=custom_params
        )
        return result
    else:
        # Mark executing and launch background task
        crud_pipelines.update_pipeline_run(db, run, status="EXECUTING")
        background_tasks.add_task(
            _bg_execute_pipeline,
            pipeline_id=pipeline_id,
            adapter_type=adapter_type,
            seed=seed,
            max_retries=max_retries,
            custom_params=custom_params
        )
        return PipelineOrchestrator.get_pipeline_status(db, pipeline_id)

@router.get("/runs", response_model=List[Dict[str, Any]])
def list_pipeline_runs(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """List recent pipeline runs."""
    runs = crud_pipelines.list_pipeline_runs(db, limit=limit)
    return [PipelineOrchestrator.get_pipeline_status(db, r.id) for r in runs]

@router.get("/{pipeline_id}", response_model=Dict[str, Any])
def get_pipeline(pipeline_id: str, db: Session = Depends(get_db)):
    """Get complete pipeline status including all decomposed scenes and QA scores."""
    try:
        return PipelineOrchestrator.get_pipeline_status(db, pipeline_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{pipeline_id}/scenes", response_model=List[Dict[str, Any]])
def get_pipeline_scenes(pipeline_id: str, db: Session = Depends(get_db)):
    """Get individual scene results for a pipeline run."""
    try:
        status_data = PipelineOrchestrator.get_pipeline_status(db, pipeline_id)
        return status_data.get("scenes", [])
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
