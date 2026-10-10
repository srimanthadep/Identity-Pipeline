import os
import logging
from pathlib import Path
from typing import Dict, Any
from app.adapters.base import GenerationAdapter
from app.config import settings

logger = logging.getLogger(__name__)

class WanFalAdapter(GenerationAdapter):
    """
    Real Wan 2.2 Image-to-Video generation adapter via Fal.ai.
    Uses verified official Fal.ai endpoint: fal-ai/wan/v2.2-a14b/image-to-video
    Requires FAL_KEY environment variable.
    """

    ENDPOINT_ID = "fal-ai/wan/v2.2-a14b/image-to-video"

    def generate(
        self,
        job_id: str,
        blueprint: Dict[str, Any],
        reference_asset_path: Path,
        output_dir: Path
    ) -> Dict[str, Any]:
        fal_key = settings.FAL_KEY or os.environ.get("FAL_KEY", "")
        if not fal_key:
            raise ValueError(
                "FAL_KEY is not configured. Set FAL_KEY in .env to use the real Wan 2.2 adapter, "
                "or use adapter_type='simulated' for local zero-cost generation."
            )

        try:
            import fal_client
        except ImportError:
            raise ImportError("fal-client package is required for Wan 2.2 integration.")

        logger.info(f"Submitting job {job_id} to Fal.ai Wan 2.2 endpoint: {self.ENDPOINT_ID}")

        # Extract verified parameters from blueprint
        gen_params = blueprint.get("generation_params", {})
        
        # In production with Fal.ai, image_url must be a public URL or uploaded via fal_client.upload_file
        # Upload local reference asset if needed
        logger.info(f"Uploading reference asset {reference_asset_path} to Fal storage...")
        image_url = fal_client.upload_file(str(reference_asset_path))

        payload = {
            "image_url": image_url,
            "prompt": gen_params.get("prompt", ""),
            "num_frames": gen_params.get("num_frames", 81),
            "frames_per_second": gen_params.get("frames_per_second", 16),
            "resolution": gen_params.get("resolution", "720p"),
            "aspect_ratio": gen_params.get("aspect_ratio", "auto"),
            "num_inference_steps": gen_params.get("num_inference_steps", 27),
            "guidance_scale": gen_params.get("guidance_scale", 3.5),
            "enable_prompt_expansion": False, # Verified: immutable identity preservation
            "negative_prompt": gen_params.get("negative_prompt", ""),
            "acceleration": gen_params.get("acceleration", "regular"),
            "video_quality": gen_params.get("video_quality", "high"),
        }
        if gen_params.get("seed") is not None:
            payload["seed"] = gen_params.get("seed")

        # Submit and subscribe
        handler = fal_client.subscribe(
            self.ENDPOINT_ID,
            arguments=payload,
            with_logs=True
        )

        result = handler
        video_info = result.get("video", {})
        video_url = video_info.get("url")

        logger.info(f"Wan 2.2 video generation complete: {video_url}")

        return {
            "output_uri": video_url,
            "is_simulated": False,
            "metadata": {
                "adapter": "wan_i2v",
                "endpoint": self.ENDPOINT_ID,
                "seed": result.get("seed"),
                "prompt_used": result.get("prompt"),
                "verified_fields": True
            }
        }
