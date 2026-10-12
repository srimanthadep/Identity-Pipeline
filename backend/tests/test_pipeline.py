import json
import pytest
from app.schemas.blueprint import (
    CameraAngle,
    ShotType,
    ScenePlan,
    VideoBlueprintPlan,
    CharacterContext,
)
from app.services.gemini_planner import GeminiBlueprintPlanner
from app.services.pipeline_orchestrator import PipelineOrchestrator
from app.crud import pipelines as crud_pipelines
from app.crud import characters as crud_characters

def test_blueprint_schema_validation():
    scene = ScenePlan(
        scene_number=1,
        scene_title="Market Entry",
        visual_description="Walking into vibrant bazaar with rich lighting",
        camera_angle=CameraAngle.FRONT,
        shot_type=ShotType.MEDIUM,
        character_action="Walking forward smiling",
        environment="Mumbai market",
        estimated_duration_seconds=5.0
    )
    blueprint = VideoBlueprintPlan(
        title="Bazaar Journey",
        total_scenes=1,
        character_id="char_01_priya",
        scenes=[scene],
        narrative_summary="A stroll through the bazaar."
    )
    raw_json = blueprint.model_dump_json()
    loaded = VideoBlueprintPlan.model_validate_json(raw_json)
    assert loaded.character_id == "char_01_priya"
    assert loaded.scenes[0].camera_angle == CameraAngle.FRONT
    assert loaded.scenes[0].shot_type == ShotType.MEDIUM

def test_gemini_planner_fallback():
    char_context = CharacterContext(
        character_id="char_01_priya",
        character_version=1,
        name="Priya",
        gender="Female",
        age_range="22-28",
        physical_traits={"skin_tone": "Warm golden-brown"},
        canonical_portrait_uri="characters/char_01_priya/portrait.png",
        reference_asset_version=1,
        identity_prompt="[IDENTITY: Priya, Female, 22-28. skin: Warm golden-brown]"
    )
    blueprint = GeminiBlueprintPlanner.plan_blueprint(
        user_prompt="Priya explores Bangalore tech park and gives a keynote speech",
        character_context=char_context
    )
    assert blueprint.character_id == "char_01_priya"
    assert blueprint.total_scenes >= 3
    assert len(blueprint.scenes) == blueprint.total_scenes
    assert blueprint.scenes[0].scene_number == 1
    # Check camera angles exist
    for sc in blueprint.scenes:
        assert isinstance(sc.camera_angle, CameraAngle)
        assert isinstance(sc.shot_type, ShotType)

def test_pipeline_orchestrator_plan_and_freeze(db_session):
    plan_resp = PipelineOrchestrator.create_plan(
        db=db_session,
        character_identifier="char_01_priya",
        user_prompt="Priya walks into an art gallery, examines paintings, and smiles"
    )
    assert plan_resp.status == "PLANNED"
    assert plan_resp.character.character_id == "char_01_priya"
    assert plan_resp.character.character_version == 1
    assert plan_resp.character.reference_asset_version == 1
    assert plan_resp.blueprint.total_scenes >= 3

    # Check database record
    run = crud_pipelines.get_pipeline_run(db_session, plan_resp.pipeline_id)
    assert run is not None
    assert run.status == "PLANNED"
    assert run.character_version == 1

def test_pipeline_multi_scene_execution_and_version_pinning(db_session):
    plan_resp = PipelineOrchestrator.create_plan(
        db=db_session,
        character_identifier="char_01_priya",
        user_prompt="Priya arrives at a fashion studio, tries on a stole, and signs a contract"
    )

    # Execute all scenes
    status_data = PipelineOrchestrator.execute_pipeline(
        db=db_session,
        pipeline_id=plan_resp.pipeline_id,
        adapter_type="simulated"
    )

    assert status_data["status"] == "COMPLETED"
    assert status_data["completed_scenes"] == status_data["total_scenes"]
    assert len(status_data["scenes"]) == status_data["total_scenes"]

    # Verify that all generated jobs in this pipeline share identical pinned versions
    jobs = crud_pipelines.get_pipeline_jobs(db_session, plan_resp.pipeline_id)
    assert len(jobs) == status_data["total_scenes"]

    pinned_char_ver = jobs[0].character_version
    pinned_asset_ver = jobs[0].reference_asset_version
    pinned_asset_uri = jobs[0].reference_asset_uri

    for job in jobs:
        # 3-Layer identity anchoring assertions
        assert job.character_version == pinned_char_ver == 1
        assert job.reference_asset_version == pinned_asset_ver == 1
        assert job.reference_asset_uri == pinned_asset_uri
        assert job.status == "COMPLETED"
        assert job.output_uri is not None
        assert job.is_simulated == 1  # Simulated mode honestly labeled
        # Verify camera angle was saved and integrated into prompt
        assert job.camera_angle is not None
        assert "Camera:" in job.scene_prompt
        # Verify QA report exists per scene
        assert len(job.qa_reports) >= 1
        assert job.qa_reports[0].decision in ["PASS", "REVIEW", "FAIL"]

def test_pipeline_api_endpoints(client):
    # 1. Plan blueprint
    plan_res = client.post("/api/v1/pipeline/plan", json={
        "character_id": "char_02_arjun",
        "user_prompt": "Arjun sits at a coffee shop in Bangalore, works on laptop, and greets a colleague"
    })
    assert plan_res.status_code == 201
    plan_data = plan_res.json()
    pipeline_id = plan_data["pipeline_id"]
    assert plan_data["character"]["name"] == "Arjun"
    assert len(plan_data["blueprint"]["scenes"]) >= 3

    # 2. Execute synchronously
    exec_res = client.post(f"/api/v1/pipeline/execute/{pipeline_id}?run_sync=true", json={
        "adapter_type": "simulated"
    })
    assert exec_res.status_code == 200
    exec_data = exec_res.json()
    assert exec_data["status"] == "COMPLETED"
    assert exec_data["completed_scenes"] == exec_data["total_scenes"]

    # 3. Get pipeline status
    get_res = client.get(f"/api/v1/pipeline/{pipeline_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == pipeline_id

    # 4. Get scenes
    scenes_res = client.get(f"/api/v1/pipeline/{pipeline_id}/scenes")
    assert scenes_res.status_code == 200
    scenes_data = scenes_res.json()
    assert len(scenes_data) == exec_data["total_scenes"]
    for sc in scenes_data:
        assert sc["status"] == "COMPLETED"
        assert sc["output_url"] is not None
        assert sc["identity_score"] is not None

    # 5. List runs
    runs_res = client.get("/api/v1/pipeline/runs")
    assert runs_res.status_code == 200
    assert any(r["id"] == pipeline_id for r in runs_res.json())

def test_character_differentiation_in_pipeline(db_session):
    plan_priya = PipelineOrchestrator.create_plan(
        db=db_session,
        character_identifier="char_01_priya",
        user_prompt="Priya presents a marketing strategy"
    )
    plan_arjun = PipelineOrchestrator.create_plan(
        db=db_session,
        character_identifier="char_02_arjun",
        user_prompt="Arjun develops a mobile application"
    )

    assert plan_priya.character.character_id != plan_arjun.character.character_id
    assert "Priya" in plan_priya.character.identity_prompt
    assert "Arjun" in plan_arjun.character.identity_prompt
    assert plan_priya.character.canonical_portrait_uri != plan_arjun.character.canonical_portrait_uri
