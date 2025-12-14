import yaml
from pathlib import Path
from typing import Any, Dict

class ConfigEditorService:
    def __init__(self, project_root: Path):
        self.root = project_root
        self.env_path = self.root / ".env"
        self.app_setting_path = self.root / "config" / "appsetting.yaml"
        self.instruction_path = self.root / "config" / "instructions.yaml"

    def load_env_vars(self) -> Dict[str, str]:
        env_vars = {}
        if self.env_path.exists():
            with open(self.env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        key, val = line.strip().split("=", 1)
                        env_vars[key] = val
        return env_vars

    def save_env_vars(self, data: Dict[str, str]):
        content = ""
        for key, val in data.items():
            content += f"{key}={val}\n"
        with open(self.env_path, "w", encoding="utf-8") as f:
            f.write(content)

    def load_yaml(self, file_type: str) -> Dict[str, Any]:
        path = self.app_setting_path if file_type == "app" else self.instruction_path
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def save_yaml(self, file_type: str, data: Dict[str, Any]):
        path = self.app_setting_path if file_type == "app" else self.instruction_path
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
