from __future__ import annotations

from abc import ABC, abstractmethod


class AiService(ABC):
    @abstractmethod
    async def generateInsight(self, promptValue: str) -> str:
        raise NotImplementedError
