import os

DEFAULT_CONFIG = 'F:/Document/密钥/.seedance_config'
KEY_NAME = 'SEEDANCE_AUTH_TOKEN'


def resolve_token(value):
    """输入框有值就用输入框的值，否则读环境变量，再否则读密钥目录里的配置文件。"""
    v = (value or '').strip()
    if v:
        return v
    v = os.environ.get(KEY_NAME, '').strip()
    if v:
        return v
    p = os.environ.get('SEEDANCE_CONFIG_PATH') or DEFAULT_CONFIG
    if os.path.isfile(p):
        with open(p, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, val = line.split('=', 1)
                    if k.strip() == KEY_NAME and val.strip():
                        return val.strip()
    raise RuntimeError('Seedance: 未找到 auth_token，请在节点里填写，或设置环境变量 SEEDANCE_AUTH_TOKEN，或在 F:/Document/密钥/.seedance_config 里写入 SEEDANCE_AUTH_TOKEN=...')
