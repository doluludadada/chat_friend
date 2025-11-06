from pathlib import Path

import yaml
from src.b_application.configuration.schemas import AppConfig
from src.c_infrastructure.config.utils import get_project_root


def load_settings(config_path: Path | None = None) -> AppConfig:
    """
    Loads application settings from a YAML file and environment variables.
    """
    project_root = get_project_root()

    if config_path is None:
        config_path = project_root / "config" / "appsetting.yaml"

    config_from_yaml = {}
    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config_from_yaml = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Warning: Could not load YAML config from {config_path}. Error: {e}")
        pass

    return AppConfig(project_root=project_root, **config_from_yaml)
