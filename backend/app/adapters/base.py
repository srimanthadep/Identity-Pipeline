from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

class GenerationAdapter(ABC):
    """Abstract base class for video / frame generation adapters."""

    @abstractmethod
    def generate(
        self,
        job_id: str,
        blueprint: Dict[str, Any],
        reference_asset_path: Path,
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Execute generation based on blueprint and reference asset.
        
        Returns dict with:
            - output_uri: relative or absolute URI
            - is_simulated: boolean
            - metadata: extra provider metadata
        """
        pass
