import os
import time
import json
import requests

CATEGORY = "Agrant/Seedance"

MODEL_OPTIONS = {
    "seedance-2.0": 29,
    "seedance-2.0-fast": 30,
}


class SeedanceVideoGenerator:
    def __init__(self):
        pass

    CATEGORY = CATEGORY

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_base_url": ("STRING", {"default": "http://vtl.cue.group/"}),
                "auth_token":   ("STRING", {"default": ""}),
                "model":        (list(MODEL_OPTIONS.keys()),),
                "prompt":       ("STRING", {"multiline": True, "default": ""}),
                "resolution":   (["720p", "480p"],),
                "ratio":        (["16:9", "9:16", "1:1"],),
                "duration":     ("INT", {"default": 8, "min": 4, "max": 15}),
            },
            "optional": {
                "first_frame_url":      ("STRING", {"default": ""}),
                "last_frame_url":       ("STRING", {"default": ""}),
                "reference_image_url":  ("STRING", {"default": ""}),
                "reference_video_url":  ("STRING", {"default": ""}),
                "reference_audio_url":  ("STRING", {"default": ""}),
                "generate_audio":       ("BOOLEAN", {"default": True}),
                "watermark":            ("BOOLEAN", {"default": False}),
                "poll_interval":        ("INT", {"default": 5, "min": 2, "max": 30}),
                "timeout_seconds":      ("INT", {"default": 600, "min": 60, "max": 1800}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_url",)
    FUNCTION = "generate"
    OUTPUT_NODE = True

    def generate(self, api_base_url, auth_token, model, prompt,
                 resolution, ratio, duration,
                 first_frame_url="", last_frame_url="",
                 reference_image_url="", reference_video_url="", reference_audio_url="",
                 generate_audio=True, watermark=False,
                 poll_interval=5, timeout_seconds=600):

        base = api_base_url.rstrip("/")
        submit_url = f"{base}/model/video/task"
        query_url  = f"{base}/model/video/result"

        headers = {
            "Authorization": auth_token.strip(),
            "Content-Type": "application/json",
        }

        content = []
        if prompt.strip():
            content.append({"type": "text", "text": prompt.strip()})
        if first_frame_url.strip():
            content.append({
                "type": "image_url",
                "image_url": {"url": first_frame_url.strip()},
                "role": "first_frame",
            })
        if last_frame_url.strip():
            content.append({
                "type": "image_url",
                "image_url": {"url": last_frame_url.strip()},
                "role": "last_frame",
            })
        if reference_image_url.strip():
            content.append({
                "type": "image_url",
                "image_url": {"url": reference_image_url.strip()},
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

        payload = {
            "modelId":       MODEL_OPTIONS[model],
            "resolution":    resolution,
            "ratio":         ratio,
            "duration":      duration,
            "generateAudio": generate_audio,
            "watermark":     watermark,
            "content":       content,
        }

        print(f"[Seedance] 提交任务 → {submit_url}")
        print(f"[Seedance] content: {json.dumps(content, ensure_ascii=False)}")
        print(f"[Seedance] 请求体: {json.dumps(payload, ensure_ascii=False)}")

        resp = requests.post(submit_url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        body = resp.json()

        if body.get("code") != 2000:
            raise RuntimeError(f"[Seedance] 提交失败: {body.get('msg')} | {body}")

        task_id = body["data"]["taskId"]
        print(f"[Seedance] taskId: {task_id}，开始轮询...")

        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            time.sleep(poll_interval)
            r = requests.get(query_url, params={"taskId": task_id}, headers=headers, timeout=30)
            r.raise_for_status()
            result = r.json()

            if result.get("code") != 2000:
                raise RuntimeError(f"[Seedance] 查询失败: {result.get('msg')} | {result}")

            status = result["data"]["status"]
            print(f"[Seedance] status={status}")

            if status == 2:
                video_url = result["data"]["videoUrl"]
                print(f"[Seedance] 完成！视频 URL: {video_url}")
                return (video_url,)
            elif status == -1:
                raise RuntimeError(f"[Seedance] 视频生成失败（服务端 status=-1）| 完整响应: {result}")
            elif status == -2:
                raise RuntimeError("[Seedance] 任务已被删除（status=-2）")

        raise RuntimeError(f"[Seedance] 超时（{timeout_seconds}s 内未完成）")
