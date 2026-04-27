# ComfyUI-Seedance-API

ComfyUI custom nodes for Seedance video generation and basic video frame statistics.

## Included Nodes

- `ComfyUI-Seedance-API` (`seedance_video_generate`)
  - Calls a custom Seedance-compatible API endpoint.
- `Ark Seedance Video (官方API)` (`ark_seedance_video_generate`)
  - Calls Volcengine Ark official Seedance API.
- `mp4获取帧数` (`mp4_to_frame_rate`)
  - Reads MP4 frame count, fps, and duration.

## Installation

1. Clone this repository into your ComfyUI custom nodes directory.
2. Install dependencies:

```bash
pip install requests opencv-python
```

3. Restart ComfyUI.

## Ark Seedance Node Parameters

Main required inputs:

- `api_key`: Ark API key, usually starts with `ark-`.
- `model`: one of:
  - `doubao-seedance-2-0-260128`
  - `doubao-seedance-1-0-241228`
  - `doubao-seedance-1-0-lite-241231`
- `prompt`
- `resolution`: `480p` / `720p` / `1080p`
- `ratio`: `16:9` / `9:16` / `4:3` / `3:4` / `1:1` / `21:9` / `9:21`
- `duration`
- `generate_audio`
- `watermark`

Optional inputs:

- `first_frame_image_url`: first frame reference image URL.
- `last_frame_image_url`: last frame reference image URL.
- `reference_image_urls`: multiple image URLs separated by comma.
- `reference_video_url`
- `reference_audio_url`
- `poll_interval`
- `timeout_seconds`

Notes:

- At least one of `prompt` or reference media URLs must be provided.
- When `reference_video_url` is provided (r2v mode), `resolution` is not sent.

## Seedance Video Node Parameters

Main required inputs:

- `api_base_url`
- `auth_token`
- `model`: `seedance-2.0` or `seedance-2.0-fast`
- `prompt`
- `resolution`: `1080P` / `720p` / `480p`
- `ratio`: `16:9` / `9:16` / `1:1`
- `duration`

Optional inputs:

- `first_frame_url`
- `last_frame_url`
- `reference_image_url`
- `reference_video_url`
- `reference_audio_url`
- `generate_audio`
- `watermark`
- `poll_interval`
- `timeout_seconds`

Notes:

- `seedance-2.0-fast` does not support `1080P`.
- At least one of `prompt` or reference media URLs must be provided.

## mp4_to_frame_rate Node

Input:

- `video_path`

Output:

- `frame_count` (INT)
- `fps` (FLOAT)
- `duration_seconds` (FLOAT)

## Category

- `Agrant/Seedance`
- `Agrant/Video`
