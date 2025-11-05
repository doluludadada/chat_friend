set windows-shell := ["powershell", "-Command"]

dev-sync:
    uv sync --all-extras --cache-dir .uv_cache

format:
	uv run ruff format