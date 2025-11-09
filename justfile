set windows-shell := ["powershell", "-Command"]

active_venv:
    .venv\Scripts\Activate.ps1
    
dev-sync:
    uv sync --all-extras

format:
	uv run ruff format

ngrok:
    ngrok http 8000

run:
    uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

