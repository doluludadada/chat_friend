import sys
from fastapi import FastAPI
from src.d_presentation.container import Container
from src.d_presentation.web.api_router import api_router

def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application and its resources.
    """
    # Instantiate the dependency injection container.
    container = Container()

    # Wire the container to the modules that need dependency injection.
    # This is a crucial step that enables the @inject decorator and Depends(Provide[...]) to work.
    # We specify the modules where injection will happen.
    container.wire(modules=[
        sys.modules[__name__],
        "src.c_infrastructure.platforms.line.line_webhook_router"
    ])

    # Create the main FastAPI application instance.
    app = FastAPI(
        title="ChatFriend AI Assistant",
        description="An AI chat assistant service for WhatsApp and Line.",
        version="0.1.0",
    )

    # Attach the container to the app's state for potential access elsewhere.
    app.state.container = container
    
    # Include the main API router.
    app.include_router(api_router)

    return app
