def test_create_and_execute_generation_job_api(client):
    payload = {
        "character_id": "char_01_priya",
        "scene_prompt": "Giving a keynote presentation at a tech summit in Hyderabad",
        "adapter_type": "simulated",
        "seed": 42
    }
    # Run sync to get immediate result in test
    response = client.post("/api/v1/generations?run_sync=true", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["is_simulated"] is True
    assert data["character_version"] == 1
    assert data["reference_asset_version"] == 1
    assert data["output_url"] is not None
    assert len(data["qa_reports"]) >= 1

    job_id = data["id"]

    # Fetch by ID
    get_res = client.get(f"/api/v1/generations/{job_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == job_id

    # Fetch QA report
    qa_res = client.get(f"/api/v1/generations/{job_id}/qa")
    assert qa_res.status_code == 200
    reports = qa_res.json()
    assert len(reports) >= 1
    assert reports[0]["decision"] in ["PASS", "FAIL", "REVIEW"]

    # Fetch character generation history
    hist_res = client.get("/api/v1/generations/by-character/char_01_priya")
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) >= 1
    assert history[0]["id"] == job_id
