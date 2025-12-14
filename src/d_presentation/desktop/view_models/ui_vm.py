import threading
import time
from typing import Callable

from src.c_infrastructure.config.loader import get_project_root
from src.c_infrastructure.services.ui.config_editor import ConfigEditorService
from src.c_infrastructure.services.ui.process_manager import ProcessManager


class AdminViewModel:
    def __init__(self):
        self.root = get_project_root()
        self.config_service = ConfigEditorService(self.root)
        self.process_manager = ProcessManager()
        self.on_log_received: Callable[[str], None] | None = None
        self._monitor_thread = None

    def load_data(self):
        env = self.config_service.load_env_vars()
        app_conf = self.config_service.load_yaml("app")
        instruct_conf = self.config_service.load_yaml("instruction")
        return env, app_conf, instruct_conf

    def save_all(self, env: dict, app_conf: dict, instruct_conf: dict):
        self.config_service.save_env_vars(env)
        self.config_service.save_yaml("app", app_conf)
        self.config_service.save_yaml("instruction", instruct_conf)

    def toggle_server(self):
        if self.process_manager.is_running:
            self.process_manager.stop_server()
        else:
            self.process_manager.start_server(self.root)
            self._start_log_monitor()

    def _start_log_monitor(self):
        if self._monitor_thread and self._monitor_thread.is_alive():
            return
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def _monitor_loop(self):
        while self.process_manager.is_running:
            line = self.process_manager.get_output_line()
            if line and self.on_log_received:
                self.on_log_received(line)
            else:
                time.sleep(0.1)
