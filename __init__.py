from .seedance_video import SeedanceVideoGenerator
from .mp4_to_frame_rate import mp4_to_frame_rate
from .ark_seedance_video import ArkSeedanceVideoGenerator
from .asset_upload import SeedanceAssetUpload, SeedanceVideoAssetUpload

NODE_CLASS_MAPPINGS = {
    "seedance_video_generate": SeedanceVideoGenerator,
    "mp4_to_frame_rate": mp4_to_frame_rate,
    "ark_seedance_video_generate": ArkSeedanceVideoGenerator,
    "seedance_asset_upload": SeedanceAssetUpload,
    "seedance_video_asset_upload": SeedanceVideoAssetUpload,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "seedance_video_generate": "ComfyUI-Seedance-API",
    "mp4_to_frame_rate": "mp4获取帧数",
    "ark_seedance_video_generate": "Ark Seedance Video (官方API)",
    "seedance_asset_upload": "Seedance 素材上传 (图片URL→asset)",
    "seedance_video_asset_upload": "Seedance 素材上传 (视频URL→asset)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
