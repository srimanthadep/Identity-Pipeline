import pytest
from app.services.generation_service import GenerationService
from app.crud.characters import get_character_by_id_or_slug, get_canonical_portrait_asset
from app.crud.generations import get_generation_job

def test_version_pinning_on_job_creation(db_session):
    char = get_character_by_id_or_slug(db_session, "char_04_raj")
    asset = get_canonical_portrait_asset(db_session, char.id)
    
    assert char.version == 1
    assert asset.version == 1

    job_data = GenerationService.create_generation_job(
        db=db_session,
        character_identifier="char_04_raj",
        scene_prompt="Delivering a pitch at Bangalore startup incubator"
    )

    assert job_data["character_version"] == 1
    assert job_data["reference_asset_version"] == 1
    assert job_data["reference_asset_uri"] == asset.storage_uri

def test_version_pinning_unaffected_by_character_and_asset_updates(db_session):
    # 1. Create Job #1
    job1_data = GenerationService.create_generation_job(
        db=db_session,
        character_identifier="char_02_arjun",
        scene_prompt="Training in a modern high-altitude gym"
    )

    # 2. Update character version
    char = get_character_by_id_or_slug(db_session, "char_02_arjun")
    char.version = 2
    char.name = "Arjun Verma"
    
    # Update canonical asset version
    asset = get_canonical_portrait_asset(db_session, char.id)
    asset.version = 3
    asset.storage_uri = "characters/char_02_arjun/portrait_v3.png"
    db_session.commit()

    # 3. Create Job #2 (which should pick up the new versions)
    job2_data = GenerationService.create_generation_job(
        db=db_session,
        character_identifier="char_02_arjun",
        scene_prompt="Running alongside Marine Drive at dawn"
    )

    # Verify Job #1 strictly retains pinned version 1
    reloaded_job1 = get_generation_job(db_session, job1_data["id"])
    assert reloaded_job1.character_version == 1
    assert reloaded_job1.reference_asset_version == 1
    assert reloaded_job1.reference_asset_uri == "characters/char_02_arjun/portrait.png"

    # Verify Job #2 pinned the new versions
    reloaded_job2 = get_generation_job(db_session, job2_data["id"])
    assert reloaded_job2.character_version == 2
    assert reloaded_job2.reference_asset_version == 3
    assert reloaded_job2.reference_asset_uri == "characters/char_02_arjun/portrait_v3.png"

def test_version_pinning_preserved_during_retries(db_session):
    # Create initial job
    job_data = GenerationService.create_generation_job(
        db=db_session,
        character_identifier="char_01_priya",
        scene_prompt="Leading a design sprint review",
        max_retries=2
    )
    job_id = job_data["id"]

    # Now simulate character version bump to v5 before retry
    char = get_character_by_id_or_slug(db_session, "char_01_priya")
    char.version = 5
    asset = get_canonical_portrait_asset(db_session, char.id)
    asset.version = 7
    asset.storage_uri = "characters/char_01_priya/portrait_v7.png"
    db_session.commit()

    # Execute retry
    retried_job = GenerationService.retry_job(db_session, job_id)

    # Ensure retried job still has original pinned versions 1 and 1
    assert retried_job["retry_count"] == 1
    assert retried_job["character_version"] == 1
    assert retried_job["reference_asset_version"] == 1
    assert retried_job["reference_asset_uri"] == "characters/char_01_priya/portrait.png"

def test_max_retries_boundary_enforced(db_session):
    job_data = GenerationService.create_generation_job(
        db=db_session,
        character_identifier="char_01_priya",
        scene_prompt="Scene",
        max_retries=1
    )
    job_id = job_data["id"]

    # First retry succeeds
    GenerationService.retry_job(db_session, job_id)

    # Second retry exceeds max_retries (1) and must fail
    with pytest.raises(ValueError, match="Maximum retry limit"):
        GenerationService.retry_job(db_session, job_id)
