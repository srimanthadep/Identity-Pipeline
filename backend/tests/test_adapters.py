from pathlib import Path
from PIL import Image
from app.adapters.simulated import SimulatedAdapter
from app.config import settings

def test_simulated_adapter_generates_watermarked_image(tmp_path):
    adapter = SimulatedAdapter()
    ref_portrait = settings.ASSETS_DIR / "characters" / "char_01_priya" / "portrait.png"
    
    assert ref_portrait.exists()

    blueprint = {
        "character_id": "char_01_priya",
        "scene_block": {
            "raw_prompt": "Walking inside a sunlit Bangalore tech park",
            "augmented_prompt": "Augmented prompt text"
        },
        "generation_params": {"resolution": "720p", "seed": 123}
    }

    result = adapter.generate(
        job_id="test_sim_job_001",
        blueprint=blueprint,
        reference_asset_path=ref_portrait,
        output_dir=tmp_path
    )

    assert result["is_simulated"] is True
    assert "outputs/test_sim_job_001_simulated.png" in result["output_uri"]

    out_file = tmp_path / "test_sim_job_001_simulated.png"
    assert out_file.exists()

    with Image.open(out_file) as generated:
        assert generated.size[0] > 0
        assert generated.size[1] > 0
