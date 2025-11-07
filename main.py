import uvicorn
from src.d_presentation.web.app import create_app

app = create_app()

def main():
    """
    Main entry point for the application.
    Starts the Uvicorn server.
    """
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Set to False in production
        log_level="info",
    )

if __name__ == '__main__':
    main()
