import json
import time
import requests

CATEGORY = "Agrant/Seedance"

ARK_API_BASE = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"

MODEL_OPTIONS = [
    "doubao-seedance-2-0-260128",
    "doubao-seedance-1-0-241228",
    "doubao-seedance-1-0-lite-241231",
]


class ArkSeedanceVideoGenerator:
    def __init__(self):
        pass

    CATEGORY = CATEGORY

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key":        ("STRING", {"default": "ark-"}),
                "model":          (MODEL_OPTIONS,),
                "prompt":         ("STRING", {"multiline": True, "default": ""}),
                "resolution":     (["480p", "720p", "1080p"],),
                "ratio":          (["16:9", "9:16", "4:3", "3:4", "1:1", "21:9", "9:21"],),
                "duration":       ("INT", {"default": 8, "min": 4, "max": 60}),
                "generate_audio": ("BOOLEAN", {"default": True}),
                "watermark":      ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "first_frame_image_url":  ("STRING", {"default": ""}),
                "reference_image_urls":   ("STRING", {"default": "", "tooltip": "多个 URL 用英文逗号分隔"}),
                "reference_video_url":    ("STRING", {"default": ""}),
                "reference_audio_url":    ("STRING", {"default": ""}),
                "poll_interval":          ("INT", {"default": 10, "min": 3, "max": 60}),
                "timeout_seconds":        ("INT", {"default": 900, "min": 60, "max": 3600}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_url",)
    FUNCTION = "generate"
    OUTPUT_NODE = True

    def generate(self, api_key, model, prompt, resolution, ratio, duration,
                 generate_audio, watermark,
                 first_frame_image_url="", reference_image_urls="",
                 reference_video_url="", reference_audio_url="",
                 poll_interval=10, timeout_seconds=900):

        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json",
        }

        content = []

        if prompt.strip():
            content.append({"type": "text", "text": prompt.strip()})

        if first_frame_image_url.strip():
            content.append({
                "type": "image_url",
                "image_url": {"url": first_frame_image_url.strip()},
                "role": "first_frame",
            })

        for url in [u.strip() for u in reference_image_urls.split(",") if u.strip()]:
            content.append({
                "type": "image_url",
                "image_url": {"url": url},
                "role": "reference_image",
            })

        if reference_video_url.strip():
            content.append({
                "type": "video_url",
                "video_url": {"url": reference_video_url.strip()},
                "role": "reference_video",
            })

        if reference_audio_url.strip():
            content.append({
                "type": "audio_url",
                "audio_url": {"url": reference_audio_url.strip()},
                "role": "reference_audio",
            })

        if not content:
            raise ValueError("[ArkSeedance] content 不能为空，至少填写 prompt 或任一参考素材 URL")

        payload = {
            "model": model,
            "content": content,
            "generate_audio": generate_audio,
            "ratio": ratio,
            "duration": duration,
            "watermark": watermark,
        }
        # r2v 模式（有参考视频）不支持 resolution
        if not reference_video_url.strip():
            payload["resolution"] = resolution

        print(f"[ArkSeedance] 提交任务 -> {ARK_API_BASE}")
        print(f"[ArkSeedance] payload: {json.dumps(payload, ensure_ascii=False)}")

        resp = requests.post(ARK_API_BASE, json=payload, headers=headers, timeout=30)
        if not resp.ok:
            raise RuntimeError(f"[ArkSeedance] 提交失败 {resp.status_code}: {resp.text}")
        body = resp.json()
        print(f"[ArkSeedance] 提交响应: {body}")

        task_id = body.get("id")
        if not task_id:
            raise RuntimeError(f"[ArkSeedance] 提交失败，未获得 task_id: {body}")

        print(f"[ArkSeedance] task_id={task_id}，开始轮询...")

        poll_url = f"{ARK_API_BASE}/{task_id}"
        deadline = time.time() + timeout_seconds

        while time.time() < deadline:
            time.sleep(poll_interval)
            r = requests.get(poll_url, headers=headers, timeout=30)
            r.raise_for_status()
            result = r.json()

            status = result.get("status", "")
            print(f"[ArkSeedance] status={status}")

            if status == "succeeded":
                print(f"[ArkSeedance] 完整响应: {result}")
                content = result.get("content", {})
                # content 是 dict: {"video_url": "https://..."}
                if isinstance(content, dict) and content.get("video_url"):
                    video_url = content["video_url"]
                    print(f"[ArkSeedance] 完成！视频 URL: {video_url}")
                    return (video_url,)
                raise RuntimeError(f"[ArkSeedance] 状态 succeeded 但未找到 video_url，完整响应: {result}")

            if status == "failed":
                error = result.get("error", {})
                raise RuntimeError(
                    f"[ArkSeedance] 任务失败 | code={error.get('code')} "
                    f"message={error.get('message')} | 完整响应: {result}"
                )

        raise RuntimeError(f"[ArkSeedance] 超时（{timeout_seconds}s 内未完成），task_id={task_id}")
