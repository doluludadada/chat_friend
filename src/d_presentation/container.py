from dependency_injector import containers, providers
from src.b_application.configuration.schemas import AppConfig
from src.b_application.use_cases.conversation_usecase import ConversationUsecase
from src.c_infrastructure.ai_models.factory import build_ai_adapter
from src.c_infrastructure.config.loader import load_settings
from src.c_infrastructure.persistence.inmemory_repository import InMemoryRepositoryAdapter
from src.c_infrastructure.platforms.line.line_adapter import LinePlatformAdapter
from src.c_infrastructure.platforms.line.line_security import LineSecurityService

from src.c_infrastructure.services.logger_service import LogggerAdapter


class Container(containers.DeclarativeContainer):

    config: providers.Provider[AppConfig] = providers.Singleton(load_settings)
    logging = providers.Singleton(LogggerAdapter, level=config.provided.log_level)
    gateways = providers.DependenciesContainer()

    gateways.ai_adapter = providers.Factory(build_ai_adapter, config=config, logger=logging)
    gateways.platform_adapter = providers.Singleton(LinePlatformAdapter, config=config, logger=logging)
    gateways.line_security = providers.Singleton(
        LineSecurityService,
        channel_secret=config.provided.line_channel_secret,
        logger=logging,
    )
    persistence = providers.DependenciesContainer()
    persistence.repository = providers.Singleton(InMemoryRepositoryAdapter, logger=logging)

    use_cases = providers.DependenciesContainer()
    use_cases.conversation_usecase = providers.Factory(
        ConversationUsecase,
        ai_port=gateways.ai_adapter,
        repository_port=persistence.repository,
        platform_port=gateways.platform_adapter,
        logging_port=logging,
    )
