from functools import lru_cache

from fastapi import Depends
from src.a_domain.ports.bussiness.ai_port import AiPort
from src.a_domain.ports.bussiness.chat_styler_port import IChatStylerPort
from src.a_domain.ports.bussiness.platform_port import PlatformPort
from src.a_domain.ports.bussiness.repository_port import RepositoryPort

# Ports


from src.a_domain.ports.notification.logging_port import ILoggingPort
from src.b_application.configuration.schemas import AppConfig

# Configurations


from src.b_application.pipeline import Pipeline
from src.b_application.use_cases.collect.context_loader import ContextLoader
from src.b_application.use_cases.process.ai_processor import AiProcessor
from src.b_application.use_cases.ship.dispatcher import Dispatcher
from src.b_application.use_cases.ship.state_manager import StateManager
from src.c_infrastructure.ai_models.factory import AiAdapterFactory
from src.c_infrastructure.config.loader import load_settings
from src.c_infrastructure.persistence.inmemory_repository import InMemoryRepositoryAdapter
from src.c_infrastructure.platforms.line.line_adapter import LinePlatformAdapter
from src.c_infrastructure.platforms.line.line_handler import LineWebhookHandler
from src.c_infrastructure.platforms.line.line_security import LineSecurityService
from src.c_infrastructure.services.chat_styler_service import ChatStylerService

# Adapters & Services


from src.c_infrastructure.services.logger_service import LoggerService

# Pipeline Components


@lru_cache
def get_settings() -> AppConfig:
    return load_settings()


def get_logger(settings: AppConfig = Depends(get_settings)) -> ILoggingPort:
    return LoggerService(level=settings.log_level)


def get_repository(logger: ILoggingPort = Depends(get_logger)) -> RepositoryPort:
    return InMemoryRepositoryAdapter(logger=logger)


def get_styler() -> IChatStylerPort:
    return ChatStylerService()


def get_platform_adapter(
    settings: AppConfig = Depends(get_settings), logger: ILoggingPort = Depends(get_logger)
) -> PlatformPort:
    return LinePlatformAdapter(config=settings, logger=logger)


def get_ai_adapter(settings: AppConfig = Depends(get_settings), logger: ILoggingPort = Depends(get_logger)) -> AiPort:
    factory = AiAdapterFactory(config=settings, logger=logger)
    return factory.create_adapter()


# --- Pipeline Assembly ---


def get_context_loader(
    repo: RepositoryPort = Depends(get_repository),
    config: AppConfig = Depends(get_settings),
    logger: ILoggingPort = Depends(get_logger),
) -> ContextLoader:
    return ContextLoader(repository=repo, config=config, logger=logger)


def get_ai_processor(
    ai: AiPort = Depends(get_ai_adapter),
    styler: IChatStylerPort = Depends(get_styler),
    logger: ILoggingPort = Depends(get_logger),
) -> AiProcessor:
    return AiProcessor(ai_port=ai, styler_port=styler, logger=logger)


def get_state_manager(
    repo: RepositoryPort = Depends(get_repository), logger: ILoggingPort = Depends(get_logger)
) -> StateManager:
    return StateManager(repository=repo, logger=logger)


def get_dispatcher(
    platform: PlatformPort = Depends(get_platform_adapter), logger: ILoggingPort = Depends(get_logger)
) -> Dispatcher:
    return Dispatcher(platform=platform, logger=logger)


def get_chat_pipeline(
    loader: ContextLoader = Depends(get_context_loader),
    processor: AiProcessor = Depends(get_ai_processor),
    manager: StateManager = Depends(get_state_manager),
    dispatcher: Dispatcher = Depends(get_dispatcher),
    config: AppConfig = Depends(get_settings),
) -> Pipeline:
    return Pipeline(loader, processor, manager, dispatcher, config)


# --- Webhook Handler ---


def get_line_security(
    settings: AppConfig = Depends(get_settings), logger: ILoggingPort = Depends(get_logger)
) -> LineSecurityService:
    return LineSecurityService(channel_secret=settings.line_channel_secret, logger=logger)


def get_line_handler(
    security: LineSecurityService = Depends(get_line_security), pipeline: Pipeline = Depends(get_chat_pipeline)
) -> LineWebhookHandler:
    return LineWebhookHandler(security_service=security, pipeline=pipeline)
