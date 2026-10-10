from pathlib import Path
from app.config import settings

def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "project" in data

def test_list_all_10_characters(client):
    response = client.get("/api/v1/characters")
    assert response.status_code == 200
    characters = response.json()
    assert len(characters) == 10
    
    char_ids = [c["character_id"] for c in characters]
    expected_ids = [
        "char_01_priya", "char_02_arjun", "char_03_devi", "char_04_raj",
        "char_05_ananya", "char_06_vikram", "char_07_meera", "char_08_kiran",
        "char_09_lakshmi", "char_10_aditya"
    ]
    for exp in expected_ids:
        assert exp in char_ids

def test_character_detail_and_canonical_portrait(client):
    response = client.get("/api/v1/characters/char_01_priya")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Priya"
    assert data["canonical_portrait_url"] is not None
    assert "/assets/characters/char_01_priya/portrait.png" in data["canonical_portrait_url"]
    assert "skin_tone" in data["physical_traits"]

def test_character_assets_endpoint(client):
    response = client.get("/api/v1/characters/char_02_arjun/assets")
    assert response.status_code == 200
    assets = response.json()
    assert len(assets) >= 1
    assert any(a["is_canonical"] for a in assets)

def test_character_not_found(client):
    response = client.get("/api/v1/characters/non_existent_char")
    assert response.status_code == 404

def test_disk_portrait_files_exist():
    expected_ids = [
        "char_01_priya", "char_02_arjun", "char_03_devi", "char_04_raj",
        "char_05_ananya", "char_06_vikram", "char_07_meera", "char_08_kiran",
        "char_09_lakshmi", "char_10_aditya"
    ]
    for cid in expected_ids:
        portrait_path = settings.ASSETS_DIR / "characters" / cid / "portrait.png"
        assert portrait_path.exists(), f"Portrait missing for {cid} at {portrait_path}"
