import json
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Character, CharacterAsset
from app.config import settings

logger = logging.getLogger(__name__)

CHARACTERS_DATA = [
    {
        "character_id": "char_01_priya",
        "name": "Priya",
        "gender": "Female",
        "age_range": "22-28",
        "description": "Young Indian corporate professional; sharp, poised, and approachable.",
        "physical_traits": {
            "skin_tone": "Warm golden-brown",
            "hair_color": "Deep black",
            "hair_style": "Long wavy locks falling over shoulders",
            "eye_color": "Warm dark brown",
            "facial_features": "High cheekbones, bright expressive eyes, warm engaging smile",
            "default_attire": "Navy blue blazer with fine Indian embroidery accents",
            "distinguishing_marks": "Small gold hoop earrings"
        }
    },
    {
        "character_id": "char_02_arjun",
        "name": "Arjun",
        "gender": "Male",
        "age_range": "25-32",
        "description": "Athletic and disciplined fitness consultant and model.",
        "physical_traits": {
            "skin_tone": "Medium warm brown",
            "hair_color": "Jet black",
            "hair_style": "Short cropped fade",
            "eye_color": "Dark brown",
            "facial_features": "Strong chiseled jawline, neat light stubble, focused gaze",
            "default_attire": "Charcoal athletic crewneck",
            "distinguishing_marks": "Defined athletic neck line"
        }
    },
    {
        "character_id": "char_03_devi",
        "name": "Devi",
        "gender": "Female",
        "age_range": "45-55",
        "description": "Distinguished and graceful Indian matriarch and academic.",
        "physical_traits": {
            "skin_tone": "Olive warm tan",
            "hair_color": "Dark with distinguished silver streaks",
            "hair_style": "Traditional elegant bun",
            "eye_color": "Deep warm brown",
            "facial_features": "Gentle smile lines, serene wise gaze, small red bindi",
            "default_attire": "Deep maroon handloom silk saree with gold zari",
            "distinguishing_marks": "Traditional nose stud, delicate gold chain"
        }
    },
    {
        "character_id": "char_04_raj",
        "name": "Raj",
        "gender": "Male",
        "age_range": "30-40",
        "description": "Polished tech founder and product visionary.",
        "physical_traits": {
            "skin_tone": "Light warm brown",
            "hair_color": "Black with slight wave",
            "hair_style": "Neatly parted contemporary cut",
            "eye_color": "Dark brown",
            "facial_features": "Neatly groomed full beard, tortoiseshell glasses, confident smile",
            "default_attire": "Light blue button-down Oxford shirt",
            "distinguishing_marks": "Designer spectacles"
        }
    },
    {
        "character_id": "char_05_ananya",
        "name": "Ananya",
        "gender": "Female",
        "age_range": "18-24",
        "description": "Vibrant, creative Gen-Z university student and content creator.",
        "physical_traits": {
            "skin_tone": "Medium golden",
            "hair_color": "Natural jet black",
            "hair_style": "Voluminous shoulder-length curls",
            "eye_color": "Bright sparkling brown",
            "facial_features": "Radiant wide smile, youthful rounded features, subtle hoop earrings",
            "default_attire": "Denim jacket over warm mustard tee",
            "distinguishing_marks": "Silver bracelet, natural curls"
        }
    },
    {
        "character_id": "char_06_vikram",
        "name": "Vikram",
        "gender": "Male",
        "age_range": "50-60",
        "description": "Distinguished elder, veteran educator, and mentor.",
        "physical_traits": {
            "skin_tone": "Sun-weathered medium brown",
            "hair_color": "Salt and pepper silver",
            "hair_style": "Short wavy distinguished style",
            "eye_color": "Deep honey-brown",
            "facial_features": "Thoughtful crinkles around eyes, trimmed silver mustache",
            "default_attire": "Off-white raw silk Nehru jacket over crisp white kurta",
            "distinguishing_marks": "Gold signet ring"
        }
    },
    {
        "character_id": "char_07_meera",
        "name": "Meera",
        "gender": "Female",
        "age_range": "28-35",
        "description": "Expressive visual artist and independent illustrator.",
        "physical_traits": {
            "skin_tone": "Warm wheatish",
            "hair_color": "Dark brown",
            "hair_style": "Textured wavy bun with artistic hairpin",
            "eye_color": "Expressive amber-brown",
            "facial_features": "Sculpted cheekbones, playful smile, artistic artisan jewelry",
            "default_attire": "Indigo block-printed handloom kurta",
            "distinguishing_marks": "Handcrafted terracotta earrings"
        }
    },
    {
        "character_id": "char_08_kiran",
        "name": "Kiran",
        "gender": "Non-binary",
        "age_range": "20-28",
        "description": "Contemporary minimalist designer and sound producer.",
        "physical_traits": {
            "skin_tone": "Smooth neutral brown",
            "hair_color": "Natural black",
            "hair_style": "Modern textured undercut crop",
            "eye_color": "Dark brown",
            "facial_features": "Clean androgynous bone structure, calm introspective gaze",
            "default_attire": "Sand-beige fitted mock turtleneck",
            "distinguishing_marks": "Minimalist double lobe ear studs"
        }
    },
    {
        "character_id": "char_09_lakshmi",
        "name": "Lakshmi",
        "gender": "Female",
        "age_range": "35-45",
        "description": "Classical Bharatanatyam dancer and cultural exponent.",
        "physical_traits": {
            "skin_tone": "Warm golden",
            "hair_color": "Glossy raven black",
            "hair_style": "Classical dance bun adorned with fresh white jasmine",
            "eye_color": "Large expressive almond eyes with subtle kohl",
            "facial_features": "Regal posture, defined arches, traditional maroon bindi",
            "default_attire": "Emerald green silk saree with gold zari",
            "distinguishing_marks": "Traditional temple jhumkas, alta touch"
        }
    },
    {
        "character_id": "char_10_aditya",
        "name": "Aditya",
        "gender": "Male",
        "age_range": "22-30",
        "description": "Adventurous expedition guide and landscape photographer.",
        "physical_traits": {
            "skin_tone": "Sun-bronzed golden-brown",
            "hair_color": "Dark espresso",
            "hair_style": "Tousled natural waves",
            "eye_color": "Warm amber-brown",
            "facial_features": "Warm charismatic grin, light adventure stubble",
            "default_attire": "Olive green outdoor henley",
            "distinguishing_marks": "Beaded wrist cord"
        }
    }
]

def seed_database(db: Session) -> int:
    """Idempotently seed the 10 canonical avatars and portrait assets."""
    created_count = 0
    for char_info in CHARACTERS_DATA:
        char_id = char_info["character_id"]
        
        # Check if character exists
        character = db.query(Character).filter(Character.character_id == char_id).first()
        if not character:
            character = Character(
                character_id=char_id,
                name=char_info["name"],
                description=char_info["description"],
                physical_traits=json.dumps(char_info["physical_traits"]),
                gender=char_info["gender"],
                age_range=char_info["age_range"],
                version=1
            )
            db.add(character)
            db.flush()
            created_count += 1
            logger.info(f"Created character: {char_id}")
        else:
            logger.info(f"Character already exists: {char_id}")
            
        # Check canonical portrait asset
        portrait_rel_path = f"characters/{char_id}/portrait.png"
        portrait_full_path = settings.ASSETS_DIR / portrait_rel_path
        
        canonical_asset = db.query(CharacterAsset).filter(
            CharacterAsset.character_id == character.id,
            CharacterAsset.asset_type == "portrait",
            CharacterAsset.is_canonical == 1
        ).first()
        
        if not canonical_asset:
            asset = CharacterAsset(
                character_id=character.id,
                asset_type="portrait",
                storage_uri=portrait_rel_path,
                mime_type="image/png",
                is_canonical=1,
                version=1
            )
            db.add(asset)
            logger.info(f"Registered canonical portrait for {char_id}")
            
    db.commit()
    return created_count
