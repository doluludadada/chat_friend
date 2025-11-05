from pathlib import Path

import yaml
from src.b_application.configuration.schemas import AppConfig


def load_settings(config_path: Path | None = None) -> AppConfig:
    if config_path is None:
        base_dir = Path(__file__).resolve().parents[3]
        config_path = base_dir / "config" / "appsetting.yaml"
    config_from_yaml = {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_from_yaml = yaml.safe_load(f) or {}
    except Exception:
        pass

    return AppConfig(**config_from_yaml)
