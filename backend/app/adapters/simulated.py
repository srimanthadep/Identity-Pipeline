import logging
from pathlib import Path
from typing import Dict, Any
from PIL import Image, ImageDraw, ImageFont
from app.adapters.base import GenerationAdapter

logger = logging.getLogger(__name__)

class SimulatedAdapter(GenerationAdapter):
    """
    Simulated Generation Adapter for zero-cost, local identity pipeline testing.
    Produces high-fidelity composited frames with MANDATORY [SIMULATED] watermark
    and metadata overlays to ensure honest labelling.
    """

    def generate(
        self,
        job_id: str,
        blueprint: Dict[str, Any],
        reference_asset_path: Path,
        output_dir: Path
    ) -> Dict[str, Any]:
        logger.info(f"Executing simulated generation for job {job_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        out_filename = f"{job_id}_simulated.png"
        out_filepath = output_dir / out_filename

        # Load reference asset
        if not reference_asset_path.exists():
            raise FileNotFoundError(f"Reference asset not found at {reference_asset_path}")

        with Image.open(reference_asset_path) as base_img:
            img = base_img.convert("RGBA")
            width, height = img.size

            # Create an overlay for watermark and simulation banners
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            # 1. Top banner: PROMINENT [SIMULATED] WATERMARK
            banner_height = max(50, int(height * 0.08))
            draw.rectangle([(0, 0), (width, banner_height)], fill=(200, 40, 40, 210))
            
            # Simple fallback font or default font
            try:
                # Try default PIL font
                font = ImageFont.load_default()
            except Exception:
                font = None

            draw.text(
                (15, banner_height // 4),
                "⚠️ [SIMULATED SYNTHESIS] - IDENTITY PIPELINE DEMO (LOCAL ZERO-COST)",
                fill=(255, 255, 255, 255),
                font=font
            )

            # 2. Bottom scene prompt overlay
            bottom_banner_height = max(70, int(height * 0.12))
            draw.rectangle(
                [(0, height - bottom_banner_height), (width, height)],
                fill=(15, 23, 42, 220)
            )

            char_id = blueprint.get("character_id", "Character")
            scene_text = blueprint.get("scene_block", {}).get("raw_prompt", "Scene")
            if len(scene_text) > 80:
                scene_text = scene_text[:77] + "..."

            draw.text(
                (15, height - bottom_banner_height + 10),
                f"CHARACTER: {char_id}  |  STATUS: IDENTITY PRESERVED",
                fill=(245, 158, 11, 255),
                font=font
            )
            draw.text(
                (15, height - bottom_banner_height + 35),
                f"SCENE: \"{scene_text}\"",
                fill=(241, 245, 249, 255),
                font=font
            )

            # 3. Watermark badge on bottom right
            draw.rectangle(
                [(width - 160, height - bottom_banner_height - 35), (width - 10, height - bottom_banner_height - 5)],
                fill=(0, 0, 0, 180)
            )
            draw.text(
                (width - 150, height - bottom_banner_height - 25),
                "[SIMULATED]",
                fill=(251, 191, 36, 255),
                font=font
            )

            # Composite and save
            composited = Image.alpha_composite(img, overlay)
            composited.convert("RGB").save(out_filepath, "PNG")

        rel_output_uri = f"outputs/{out_filename}"
        logger.info(f"Simulated output saved to {out_filepath}")

        return {
            "output_uri": rel_output_uri,
            "is_simulated": True,
            "metadata": {
                "adapter": "simulated",
                "watermark_applied": True,
                "resolution": blueprint.get("generation_params", {}).get("resolution", "720p"),
                "seed": blueprint.get("generation_params", {}).get("seed")
            }
        }
