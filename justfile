set windows-shell := ["powershell", "-Command"]

active_venv:
    .venv\Scripts\Activate.ps1
    
dev-sync:
    uv sync --all-extras

format:
	uv run ruff format

ngrok:
    ngrok http 8800

run:
    uv run uvicorn main:app --host 0.0.0.0 --port 8800 --reload

runui:
    uv run -m src.d_presentation.desktop.app

build-docker:
    docker build -t chat-friend .

run-docker:
    docker run -p 8000:8000 --env-file .env chat-friend
