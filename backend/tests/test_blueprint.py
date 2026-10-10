from app.services.blueprint_generator import BlueprintGenerator

def test_blueprint_generator_verified_wan_parameters():
    traits = {"skin_tone": "Warm golden", "hair_style": "Curls"}
    bp = BlueprintGenerator.generate_blueprint(
        character_id="char_05_ananya",
        character_name="Ananya",
        gender="Female",
        age_range="18-24",
        physical_traits=traits,
        scene_prompt="Studying in an outdoor library courtyard",
        reference_image_uri="characters/char_05_ananya/portrait.png",
        seed=42
    )

    assert bp["character_id"] == "char_05_ananya"
    params = bp["generation_params"]
    
    # Official Wan 2.2 verified parameters
    assert params["num_frames"] == 81
    assert params["frames_per_second"] == 16
    assert params["resolution"] == "720p"
    assert params["guidance_scale"] == 3.5
    assert params["num_inference_steps"] == 27
    assert params["enable_prompt_expansion"] is False  # Must be False for identity preservation
    assert params["seed"] == 42
    assert "prompt" in params
    assert "image_url" in params

def test_cannot_override_prompt_expansion_to_true():
    traits = {"skin_tone": "Warm golden"}
    # Even if someone attempts to pass enable_prompt_expansion=True in custom params, it must be protected
    bp = BlueprintGenerator.generate_blueprint(
        character_id="char_05_ananya",
        character_name="Ananya",
        gender="Female",
        age_range="18-24",
        physical_traits=traits,
        scene_prompt="Scene",
        reference_image_uri="uri",
        custom_params={"enable_prompt_expansion": True, "custom_field": "val"}
    )
    assert bp["generation_params"]["enable_prompt_expansion"] is False
    assert bp["generation_params"]["custom_field"] == "val"
