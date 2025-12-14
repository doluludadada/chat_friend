import subprocess
import sys
import psutil
from pathlib import Path
from typing import Optional

class ProcessManager:
    def __init__(self):
        # Type hint helps Pylance understand this can be Popen or None
        self._process: Optional[subprocess.Popen] = None

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def start_server(self, project_root: Path):
        if self.is_running:
            return
        
        # Use sys.executable to ensure the same python environment is used
        cmd = [sys.executable, "main.py"]
        
        self._process = subprocess.Popen(
            cmd,
            cwd=str(project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Redirect stderr to stdout to capture errors
            text=True,
            encoding="utf-8"
        )

    def stop_server(self):
        if self._process:
            try:
                # Terminate child processes (uvicorn spawns workers)
                parent = psutil.Process(self._process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
            except psutil.NoSuchProcess:
                pass
            self._process = None

    def get_output_line(self) -> str | None:
        """Non-blocking read of a single line from stdout."""
        # Fix for Pylance: Explicitly check if _process or its stdout is None
        if self._process is None or self._process.stdout is None:
            return None
            
        if self._process.poll() is not None:
            # Process has finished
            return None

        return self._process.stdout.readline()
