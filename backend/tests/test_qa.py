import json
from app.services.qa_service import QAService
from app.services.generation_service import GenerationService

def test_qa_service_threshold_evaluations(db_session):
    job_data = GenerationService.create_generation_job(
        db=db_session,
        character_identifier="char_03_devi",
        scene_prompt="Attending a classical music concert"
    )
    from app.crud.generations import get_generation_job
    job = get_generation_job(db_session, job_data["id"])

    # 1. Test PASS (score >= 0.85)
    report_pass = QAService.evaluate_job(db_session, job, forced_score=0.92)
    assert report_pass.decision == "PASS"
    assert report_pass.identity_score == 0.92
    assert report_pass.is_simulated == 1

    # 2. Test REVIEW (0.75 <= score < 0.85)
    report_review = QAService.evaluate_job(db_session, job, forced_score=0.80)
    assert report_review.decision == "REVIEW"
    assert report_review.identity_score == 0.80

    # 3. Test FAIL (score < 0.75)
    report_fail = QAService.evaluate_job(db_session, job, forced_score=0.68)
    assert report_fail.decision == "FAIL"
    assert report_fail.identity_score == 0.68

    metrics = json.loads(report_pass.metrics)
    assert "facial_similarity" in metrics
    assert metrics["pinned_character_version"] == job.character_version
