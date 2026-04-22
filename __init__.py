from .seedance_video import SeedanceVideoGenerator

NODE_CLASS_MAPPINGS = {
    "SeedanceVideoGenerator": SeedanceVideoGenerator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SeedanceVideoGenerator": "Seedance 2.0 视频生成",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
