from pathlib import Path

import yaml
from src.b_application.configuration.schemas import AppConfig


def load_settings(config_path: Path | None = None, instruction_path: Path | None = None) -> AppConfig:
    project_root = get_project_root()

    if config_path is None:
        config_path = project_root / "config" / "appsetting.yaml"
    if instruction_path is None:
        instruction_path = project_root / "config" / "instructions.yaml"
    config_from_yaml = {}
    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config_from_yaml = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Warning: Could not load YAML config from {config_path}. Error: {e}")
        pass
    instruction_data = {}
    try:
        if instruction_path.exists():
            with open(instruction_path, "r", encoding="utf-8") as f:
                instruction_data = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Warning: Could not load instruction YAML from {instruction_path}. Error: {e}")
        pass
    final_config_data = {**config_from_yaml, **instruction_data}

    if "system_prompt" in final_config_data:
        final_config_data["ai_system_prompt"] = final_config_data.pop("system_prompt")
    return AppConfig(project_root=project_root, **final_config_data)


def get_project_root() -> Path:
    """
    Finds the project root by searching upwards for the 'pyproject.toml' file.

    This approach is robust against changes in the directory structure.

    Returns:
        The Path object for the project's root directory.

    Raises:
        FileNotFoundError: If the 'pyproject.toml' file cannot be found.
    """
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise FileNotFoundError("Could not find project root. Make sure 'pyproject.toml' exists in the root directory.")
