import os
import uvicorn
from src.d_presentation.web.app import create_app

app = create_app()


def main():
    """
    Main entry point for the application.
    Starts the Uvicorn server.
    """
    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Set to False in production
        log_level="info",
    )


if __name__ == "__main__":
    main()
