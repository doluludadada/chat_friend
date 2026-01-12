# ChatFriend 🤖

[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Architecture](https://img.shields.io/badge/architecture-Clean%20Architecture-green)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Framework](https://img.shields.io/badge/FastAPI-0.121-009688.svg)](https://fastapi.tiangolo.com/)

**ChatFriend** is an enterprise-grade AI chatbot middleware designed with **Clean Architecture (Hexagonal Architecture)** principles. It serves as a unified interface bridging multiple messaging platforms (LINE, WhatsApp) with various LLM providers (OpenAI, Grok, Gemini, Groq), featuring RAG (Retrieval-Augmented Generation) capabilities and a desktop admin dashboard.

---

## 🏗 Architecture & Design Patterns

This project is structured to enforce separation of concerns, making it highly testable and maintainable.

### The Hexagonal Structure
The codebase follows a strict dependency rule: **Dependencies point inwards.**

* **`src/a_domain` (Core)**: Contains enterprise business rules, entities (`Conversation`, `Message`), and Interface Adapters (Ports). Pure Python, no external frameworks.
* **`src/b_application` (Use Cases)**: Orchestrates the flow of data. Implements the application logic (e.g., `ContextLoader`, `AiProcessor`, `Dispatcher`).
* **`src/c_infrastructure` (Adapters)**: Implementations of the ports defined in the domain.
    * **AI Models**: Adapters for OpenAI, Grok, Gemini.
    * **Persistence**: ChromaDB (Vector Store) & In-Memory repositories.
    * **Platforms**: LINE Messaging API integration.
* **`src/d_presentation` (Interface)**: Entry points to the application.
    * **Web**: FastAPI routers handling webhooks.
    * **Desktop**: Flet-based Admin Dashboard for configuration management.

### Key Features
* **Multi-Model Support**: Seamlessly switch between OpenAI (GPT-4), Grok (xAI), Google Gemini, and Llama (via Groq).
* **RAG Integration**: Built-in Web Search capability using Tavily API for real-time context injection.
* **State Management**: Conversation context handling with ChromaDB persistence.
* **Admin Console**: A GUI tool (Flet) to manage API keys, system prompts, and server status without touching config files.

---

## 🛠 Tech Stack

- **Language**: Python 3.13+
- **Web Framework**: FastAPI, Uvicorn
- **GUI Framework**: Flet (Flutter for Python)
- **AI Integration**: Google GenAI, OpenAI SDK, Groq API
- **Database**: ChromaDB (Vector Database)
- **Dependency Management**: `uv` (Astral)
- **Containerization**: Docker & Docker Compose
- **Testing**: Pytest, Pytest-Asyncio
- **Linting/Formatting**: Ruff, Black

---

## 🚀 Getting Started

### Prerequisites
* Python 3.13+
* [uv](https://github.com/astral-sh/uv) (Recommended package manager)
* Docker (Optional, for containerized deployment)

### Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/your-username/chat-friend.git](https://github.com/your-username/chat-friend.git)
    cd chat-friend
    ```

2.  **Install dependencies using uv**
    ```powershell
    # Install uv if not already installed
    powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"

    # Sync dependencies
    uv sync
    ```

3.  **Configuration**
    Create a `.env` file in the root directory:
    ```ini
    # .env example
    PORT=8800
    OPENAI_API_KEY=sk-...
    GROK_API_KEY=...
    GEMINI_API_KEY=...
    GROQ_API_KEY=...
    TAVILY_API_KEY=tvly-...
    
    # LINE Configuration
    LINE_CHANNEL_ACCESS_TOKEN=...
    LINE_CHANNEL_SECRET=...
    ```
    *Alternatively, use the **Admin Dashboard** to set these values via GUI.*

---

## 🖥 Usage

### Running the Server (API)
Start the FastAPI backend which listens for LINE webhooks.

```bash
uv run python main.py

```

The server will start at `http://0.0.0.0:8800`.
Health check endpoint: `http://localhost:8800/docs`

### Running the Admin Dashboard

Launch the desktop application to configure the server and view live logs.

```bash
uv run python src/d_presentation/desktop/app.py

```

### Running with Docker

```bash
docker-compose up --build -d

```

---

## 📂 Project Structure

```text
chat-friend/
├── config/                 # Configuration files (YAML)
├── src/
│   ├── a_domain/           # Entities, Value Objects, Port Interfaces
│   ├── b_application/      # Application Business Rules (Use Cases)
│   ├── c_infrastructure/   # Frameworks & Drivers (DB, API Clients)
│   └── d_presentation/     # Web & Desktop UI
├── tests/                  # Test suites
├── compose.yml             # Docker compose file
├── Dockerfile              # Docker build instructions
└── pyproject.toml          # Dependencies managed by uv

```

---

## 📜 License

This project is licensed under the MIT License.
