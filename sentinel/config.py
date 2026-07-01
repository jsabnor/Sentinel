import os
import re
from pathlib import Path

import yaml
from dotenv import load_dotenv

_ENV_VAR_RE = re.compile(r"\$\{(\w+)\}")


def _resolve_env(value):
    if isinstance(value, str):
        return _ENV_VAR_RE.sub(lambda m: os.environ.get(m.group(1), ""), value)
    return value


def _resolve_dict(data):
    if isinstance(data, dict):
        return {k: _resolve_dict(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_resolve_dict(v) for v in data]
    return _resolve_env(data)


def load_config(path="config.yaml"):
    load_dotenv()

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return _resolve_dict(config)
