from app.services.prompt_builder import PromptBuilder

def test_prompt_builder_identity_block():
    traits = {
        "skin_tone": "Warm golden-brown",
        "hair_style": "Long wavy locks",
        "facial_features": "High cheekbones",
        "default_attire": "Navy blue blazer"
    }
    block = PromptBuilder.build_identity_block("Priya", "Female", "22-28", traits)
    assert block["name"] == "Priya"
    assert block["gender"] == "Female"
    assert block["traits"]["skin_tone"] == "Warm golden-brown"

def test_prompt_builder_assemble_prompt():
    traits = {
        "skin_tone": "Warm brown",
        "hair_style": "Short cropped fade"
    }
    block = PromptBuilder.build_identity_block("Arjun", "Male", "25-32", traits)
    prompt = PromptBuilder.assemble_prompt(block, "Walking across a bustling Mumbai metro station")
    
    assert "[IDENTITY: Arjun, Male, 25-32." in prompt
    assert "skin: Warm brown" in prompt
    assert "[SCENE: Walking across a bustling Mumbai metro station]" in prompt
