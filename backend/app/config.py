from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root is 2 levels up from backend/app/
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    PROJECT_NAME: str = "10-Avatar Character Identity Studio"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = f"sqlite:///{WORKSPACE_ROOT / 'data' / 'identity_studio.db'}"
    
    # Asset Directories
    ASSETS_DIR: Path = WORKSPACE_ROOT / "assets"
    CHARACTERS_ASSETS_DIR: Path = WORKSPACE_ROOT / "assets" / "characters"
    OUTPUTS_DIR: Path = WORKSPACE_ROOT / "data" / "outputs"
    
    # Fal.ai
    FAL_KEY: str = ""
    DEFAULT_ADAPTER: str = "simulated"

    # Gemini Planner
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.8-flash"

settings = Settings()

# Ensure directories exist
settings.ASSETS_DIR.mkdir(parents=True, exist_ok=True)
settings.CHARACTERS_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
settings.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
(WORKSPACE_ROOT / "data").mkdir(parents=True, exist_ok=True)
