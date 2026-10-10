from app.adapters.base import GenerationAdapter
from app.adapters.simulated import SimulatedAdapter
from app.adapters.wan_fal import WanFalAdapter

def get_adapter(adapter_type: str) -> GenerationAdapter:
    if adapter_type == "wan_i2v":
        return WanFalAdapter()
    return SimulatedAdapter()

__all__ = ["GenerationAdapter", "SimulatedAdapter", "WanFalAdapter", "get_adapter"]
