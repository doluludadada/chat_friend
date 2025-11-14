# ***********************************************************************
#  Author:        Shiou
#  Created:       2025-11-13
#  Location:      src\a_domain\model\ai_provider.py
# ***********************************************************************
from dataclasses import dataclass

from src.a_domain.types.enums import AiProvider


@dataclass(frozen=True)
class AIModel:

    provider: AiProvider
    name: str  # e.g., 'gpt-5-mini'
