set windows-shell := ["powershell", "-Command"]

dev-sync:
    uv sync --all-extras --cache-dir .uv_cache

format:
	uv run ruff format

ngrok:
    ngrok http 8000

run:
    uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
