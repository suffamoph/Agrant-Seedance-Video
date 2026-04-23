from .seedance_video import SeedanceVideoGenerator
from .mp4_to_frame_rate import mp4_to_frame_rate
from .ark_seedance_video import ArkSeedanceVideoGenerator

NODE_CLASS_MAPPINGS = {
    "seedance_video_generate": SeedanceVideoGenerator,
    "mp4_to_frame_rate": mp4_to_frame_rate,
    "ark_seedance_video_generate": ArkSeedanceVideoGenerator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "seedance_video_generate": "ComfyUI-Seedance-API",
    "mp4_to_frame_rate": "mp4获取帧数",
    "ark_seedance_video_generate": "Ark Seedance Video (官方API)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
