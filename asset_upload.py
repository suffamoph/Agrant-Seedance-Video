import re
import time

import requests
from .token_utils import resolve_token

CATEGORY = "Agrant/Seedance"


def _split_urls(text):
    """按逗号 / 换行拆分为多个 URL，去空白、去空项。"""
    return [u.strip() for u in re.split(r"[,\n]", text or "") if u.strip()]


def _create_one(create_url, headers, group_id, url, name, project_name, asset_type):
    """调用 POST /model/asset/create 上传单个素材，返回 asset id。

    asset_type 取值：图片为 "Image"，视频为 "Video"。
    """
    payload = {
        "groupId": group_id,
        "url": url,
        "name": name,
        "assetType": asset_type,
        "projectName": project_name,
    }
    print(f"[SeedanceAsset] 上传素材 -> {create_url} (assetType={asset_type}, name={name}, url={url})")
    resp = requests.post(create_url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    body = resp.json()
    if body.get("code") != 2000:
        raise RuntimeError(f"[SeedanceAsset] 上传失败: {body.get('msg')} | {body}")
    asset_id = (body.get("data") or {}).get("id")
    if not asset_id:
        raise RuntimeError(f"[SeedanceAsset] 上传成功但未返回素材 id | {body}")
    return asset_id


def _wait_active(get_url, headers, asset_id, project_name, poll_interval, timeout_seconds):
    """轮询 POST /model/asset/get，直到素材 status=Active 或超时。"""
    query = {"id": asset_id, "projectName": project_name}
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            r = requests.post(get_url, json=query, headers=headers, timeout=30)
            r.raise_for_status()
            result = r.json()
            code = result.get("code")
            data = result.get("data") or {}
            status = data.get("status")
            print(f"[SeedanceAsset] status={status} (code={code})")
            if code == 2000 and status == "Active":
                return
            # 尚未就绪或临时返回非 2000，继续轮询
        except requests.RequestException as e:
            print(f"[SeedanceAsset] 查询暂时失败，重试中: {e}")
        time.sleep(poll_interval)

    print(f"[SeedanceAsset] 警告：{timeout_seconds}s 内未确认素材为 Active，"
          f"但 create 已成功，仍返回 asset://{asset_id}（可稍后自行用 asset/get 复核）")


def _upload_assets(urls, api_base_url, auth_token, name, group_id, project_name,
                   asset_type, verify_with_get, poll_interval, timeout_seconds):
    """批量上传一组 URL 为指定类型素材，返回 (asset_url, asset_id_str)。"""
    base = api_base_url.rstrip("/")
    create_url = f"{base}/model/asset/create"
    get_url = f"{base}/model/asset/get"
    headers = {
        "Authorization": resolve_token(auth_token),
        "Content-Type": "application/json",
    }
    base_name = name.strip() or "comfyui_upload"
    proj = project_name.strip() or "cue-jishu"
    gid = group_id.strip()

    asset_refs = []
    asset_ids = []
    for idx, u in enumerate(urls):
        # 多个时给每个素材名加序号，便于区分
        asset_name = base_name if len(urls) == 1 else f"{base_name}_{idx + 1}"
        asset_id = _create_one(create_url, headers, gid, u, asset_name, proj, asset_type)
        print(f"[SeedanceAsset] [{idx + 1}/{len(urls)}] 素材 id: {asset_id}")
        if verify_with_get:
            _wait_active(get_url, headers, asset_id, proj, poll_interval, timeout_seconds)
        asset_refs.append(f"asset://{asset_id}")
        asset_ids.append(asset_id)

    asset_url = ",".join(asset_refs)
    asset_id_str = ",".join(asset_ids)
    print(f"[SeedanceAsset] 完成，共 {len(urls)} 个 {asset_type}，asset_url: {asset_url}")
    return asset_url, asset_id_str


class SeedanceAssetUpload:
    """图片 URL -> 素材上传接口 -> 输出 asset:// 引用，供 Seedance 节点使用。

    对应文档 1.pdf：
      - 第 3 章 POST /model/asset/create  素材上传，一次一个 url，返回一个 asset id
      - 第 4 章 POST /model/asset/get     素材查询，确认 status=Active
    create 接口的 url 字段要求真实的 http(s) 图片地址（不接受 base64）。
    支持一次填多个 URL（逗号或换行分隔），逐个上传，输出逗号拼接的多个 asset://id。
    """

    def __init__(self):
        pass

    CATEGORY = CATEGORY

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_url":    ("STRING", {"default": "", "multiline": True,
                                            "tooltip": "一个或多个 http(s) 图片地址；多张用逗号或换行分隔"}),
                "api_base_url": ("STRING", {"default": "http://vtl.cue.group/"}),
                "auth_token":   ("STRING", {"default": ""}),
                "name":         ("STRING", {"default": "comfyui_upload"}),
            },
            "optional": {
                "group_id":         ("STRING", {"default": "group-20260716180200-2ggwq"}),
                "project_name":     ("STRING", {"default": "cue-jishu"}),
                "verify_with_get":  ("BOOLEAN", {"default": True}),
                "poll_interval":    ("INT", {"default": 3, "min": 1, "max": 30}),
                "timeout_seconds":  ("INT", {"default": 120, "min": 10, "max": 600}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("asset_url", "asset_id")
    FUNCTION = "upload"

    def upload(self, image_url, api_base_url, auth_token, name,
               group_id="group-20260716180200-2ggwq", project_name="cue-jishu",
               verify_with_get=True, poll_interval=3, timeout_seconds=120):

        urls = _split_urls(image_url)
        if not urls:
            raise ValueError("[SeedanceAsset] image_url 为空，至少填一个 http(s) 图片地址")
        for u in urls:
            if not (u.startswith("http://") or u.startswith("https://")):
                raise ValueError(f"[SeedanceAsset] image_url 必须是 http(s) 地址，收到: {u!r}")

        asset_url, asset_id_str = _upload_assets(
            urls, api_base_url, auth_token, name, group_id, project_name,
            asset_type="Image",
            verify_with_get=verify_with_get,
            poll_interval=poll_interval, timeout_seconds=timeout_seconds,
        )
        return (asset_url, asset_id_str)


# 视频文件常见扩展名，用于识别 URL 是否指向视频
_VIDEO_EXTS = (".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi", ".flv", ".ts", ".m3u8")


def _looks_like_video(url):
    """粗略判断 URL 是否指向视频（按扩展名，忽略查询参数）。"""
    path = url.split("?", 1)[0].split("#", 1)[0].lower()
    return path.endswith(_VIDEO_EXTS)


class SeedanceVideoAssetUpload:
    """视频 URL -> 素材上传接口 -> 输出 asset:// 引用，供 Seedance 视频节点使用。

    与图片素材上传节点同源，走同一套 create/get 接口，区别在于 assetType=Video。
    输出的 asset_url 可直接接到 seedance_video 节点的 reference_video_url。
    支持一次填多个 URL（逗号或换行分隔），逐个上传，输出逗号拼接的多个 asset://id。
    """

    def __init__(self):
        pass

    CATEGORY = CATEGORY

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "video_url":    ("STRING", {"default": "", "multiline": True,
                                            "tooltip": "一个或多个 http(s) 视频地址；多个用逗号或换行分隔"}),
                "api_base_url": ("STRING", {"default": "http://vtl.cue.group/"}),
                "auth_token":   ("STRING", {"default": ""}),
                "name":         ("STRING", {"default": "comfyui_video_upload"}),
            },
            "optional": {
                "group_id":         ("STRING", {"default": "group-20260716180200-2ggwq"}),
                "project_name":     ("STRING", {"default": "cue-jishu"}),
                "strict_ext_check": ("BOOLEAN", {"default": False,
                                                 "tooltip": "开启后，若 URL 扩展名不像视频则直接报错；关闭时仅打印提示"}),
                "verify_with_get":  ("BOOLEAN", {"default": True}),
                "poll_interval":    ("INT", {"default": 3, "min": 1, "max": 30}),
                # 视频转码/上传通常比图片慢，默认给更长的超时
                "timeout_seconds":  ("INT", {"default": 300, "min": 10, "max": 1800}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("asset_url", "asset_id")
    FUNCTION = "upload"

    def upload(self, video_url, api_base_url, auth_token, name,
               group_id="group-20260716180200-2ggwq", project_name="cue-jishu",
               strict_ext_check=False, verify_with_get=True,
               poll_interval=3, timeout_seconds=300):

        urls = _split_urls(video_url)
        if not urls:
            raise ValueError("[SeedanceAsset] video_url 为空，至少填一个 http(s) 视频地址")
        for u in urls:
            if not (u.startswith("http://") or u.startswith("https://")):
                raise ValueError(f"[SeedanceAsset] video_url 必须是 http(s) 地址，收到: {u!r}")
            if not _looks_like_video(u):
                msg = (f"[SeedanceAsset] URL 扩展名不像视频（支持: {', '.join(_VIDEO_EXTS)}）: {u!r}")
                if strict_ext_check:
                    raise ValueError(msg)
                print(f"{msg}；strict_ext_check=False，仍按视频素材上传")

        asset_url, asset_id_str = _upload_assets(
            urls, api_base_url, auth_token, name, group_id, project_name,
            asset_type="Video",
            verify_with_get=verify_with_get,
            poll_interval=poll_interval, timeout_seconds=timeout_seconds,
        )
        return (asset_url, asset_id_str)
