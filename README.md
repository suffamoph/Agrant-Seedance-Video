# ComfyUI-Seedance-API

ComfyUI 自定义节点，用于 Seedance 视频生成和素材上传。

## 包含的节点

- **ComfyUI-Seedance-API** (`seedance_video_generate`)
  - 调用自定义 Seedance 兼容 API 端点生成视频
- **Ark Seedance Video (官方API)** (`ark_seedance_video_generate`)
  - 调用火山引擎 Ark 官方 Seedance API 生成视频
- **Seedance 素材上传 (图片URL→asset)** (`seedance_asset_upload`)
  - 将图片 URL 上传为素材，返回 asset:// 引用
- **Seedance 素材上传 (视频URL→asset)** (`seedance_video_asset_upload`)
  - 将视频 URL 上传为素材，返回 asset:// 引用
- **mp4获取帧数** (`mp4_to_frame_rate`)
  - 读取 MP4 视频的帧数、帧率和时长

## 安装

1. 将本仓库克隆到 ComfyUI 的 custom_nodes 目录
2. 安装依赖：

```bash
pip install requests opencv-python
```

3. 重启 ComfyUI

## auth_token 配置

视频生成和素材上传节点都需要 `auth_token` 鉴权。token 按以下优先级读取：

1. **节点输入框**：如果输入框填了值，直接使用该值
2. **环境变量**：输入框为空时，读取环境变量 `SEEDANCE_AUTH_TOKEN`
3. **配置文件**：环境变量也没有时，读取 `F:/Document/密钥/.seedance_config`

配置文件格式（以 `#` 开头的行是注释）：

```ini
# 夏翔的 auth_token
SEEDANCE_AUTH_TOKEN=your_token_here
```

配置文件路径可通过环境变量 `SEEDANCE_CONFIG_PATH` 自定义。

## 视频生成节点参数

### ComfyUI-Seedance-API (`seedance_video_generate`)

**必填参数**

- `api_base_url`：API 基础地址，默认 `http://vtl.cue.group/`
- `auth_token`：鉴权 token（可留空，自动从配置读取）
- `model`：模型选择
  - `seedance-2.0`：标准版（对应内部 modelId 37）
  - `seedance-2.0-fast`：快速版（对应内部 modelId 30）
- `prompt`：文本提示词
- `resolution`：分辨率，`1080P` / `720p` / `480p`
- `ratio`：宽高比，`16:9` / `9:16` / `1:1`
- `duration`：视频时长（秒），4-15 秒

**可选参数**

- `first_frame_url`：首帧参考图 URL
- `last_frame_url`：尾帧参考图 URL
- `reference_image_url`：参考图 URL，多张用英文逗号分隔（可接素材上传节点的 asset_url 输出）
- `reference_video_url`：参考视频 URL
- `reference_audio_url`：参考音频 URL
- `generate_audio`：是否生成音频，默认 true
- `watermark`：是否加水印，默认 false
- `poll_interval`：轮询间隔（秒），默认 5
- `timeout_seconds`：超时时间（秒），默认 600

**注意事项**

- `prompt` 和参考素材至少提供一项
- `seedance-2.0-fast` 不支持 `1080P` 分辨率

### Ark Seedance Video (官方API) (`ark_seedance_video_generate`)

**必填参数**

- `api_key`：Ark API 密钥，通常以 `ark-` 开头
- `model`：模型选择
  - `doubao-seedance-2-0-260128`
  - `doubao-seedance-1-0-241228`
  - `doubao-seedance-1-0-lite-241231`
- `prompt`：文本提示词
- `resolution`：分辨率，`480p` / `720p` / `1080p`
- `ratio`：宽高比，`16:9` / `9:16` / `4:3` / `3:4` / `1:1` / `21:9` / `9:21`
- `duration`：视频时长（秒）
- `generate_audio`：是否生成音频
- `watermark`：是否加水印

**可选参数**

- `first_frame_image_url`：首帧参考图 URL
- `last_frame_image_url`：尾帧参考图 URL
- `reference_image_urls`：多个参考图 URL，用逗号分隔
- `reference_video_url`：参考视频 URL
- `reference_audio_url`：参考音频 URL
- `poll_interval`：轮询间隔（秒）
- `timeout_seconds`：超时时间（秒）

**注意事项**

- `prompt` 和参考素材至少提供一项
- 提供 `reference_video_url` 时（视频转视频模式），不发送 `resolution` 参数

## 素材上传节点参数

### Seedance 素材上传 (图片URL→asset) (`seedance_asset_upload`)

将图片 URL 上传到素材库，返回 `asset://` 格式的引用，可直接接到视频生成节点的 `reference_image_url`。

**必填参数**

- `image_url`：图片 URL，支持多张（用逗号或换行分隔）
- `api_base_url`：API 基础地址，默认 `http://vtl.cue.group/`
- `auth_token`：鉴权 token（可留空，自动从配置读取）
- `name`：素材名称，默认 `comfyui_upload`

**可选参数**

- `group_id`：素材分组 ID，默认 `group-20260716180200-2ggwq`
- `project_name`：项目名称，默认 `cue-jishu`
- `verify_with_get`：是否轮询确认素材就绪，默认 true
- `poll_interval`：轮询间隔（秒），默认 3
- `timeout_seconds`：超时时间（秒），默认 120

**输出**

- `asset_url`：逗号拼接的 asset:// 引用，可直接用于视频生成
- `asset_id`：逗号拼接的素材 ID

### Seedance 素材上传 (视频URL→asset) (`seedance_video_asset_upload`)

将视频 URL 上传到素材库，返回 `asset://` 格式的引用，可直接接到视频生成节点的 `reference_video_url`。

**必填参数**

- `video_url`：视频 URL，支持多个（用逗号或换行分隔）
- `api_base_url`：API 基础地址，默认 `http://vtl.cue.group/`
- `auth_token`：鉴权 token（可留空，自动从配置读取）
- `name`：素材名称，默认 `comfyui_video_upload`

**可选参数**

- `group_id`：素材分组 ID，默认 `group-20260716180200-2ggwq`
- `project_name`：项目名称，默认 `cue-jishu`
- `strict_ext_check`：严格检查文件扩展名，默认 false
- `verify_with_get`：是否轮询确认素材就绪，默认 true
- `poll_interval`：轮询间隔（秒），默认 3
- `timeout_seconds`：超时时间（秒），默认 300

**输出**

- `asset_url`：逗号拼接的 asset:// 引用，可直接用于视频生成
- `asset_id`：逗号拼接的素材 ID

## mp4获取帧数节点

**输入**

- `video_path`：视频文件路径

**输出**

- `frame_count` (INT)：总帧数
- `fps` (FLOAT)：帧率
- `duration_seconds` (FLOAT)：时长（秒）

## 节点分类

所有节点位于 ComfyUI 节点菜单的以下分类：

- `Agrant/Seedance`
- `Agrant/Video`
