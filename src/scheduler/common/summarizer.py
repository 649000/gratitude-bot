import logging
from abc import ABC, abstractmethod
from datetime import date

from scheduler.common.models import GratitudeEntry, User

logger = logging.getLogger(__name__)


class DigestSummarizer(ABC):
    @abstractmethod
    async def summarize(
        self,
        user: User,
        digest_type: str,
        period_start: date,
        period_end: date,
        highlights: list[GratitudeEntry],
    ) -> dict:
        raise NotImplementedError


def get_summarizer() -> DigestSummarizer:
    from scheduler.common.config import settings

    if settings.digest_summarizer == "bedrock":
        from scheduler.common.summarizer_bedrock import BedrockSummarizer

        logger.info("Using BedrockSummarizer (model=%s)", settings.bedrock_model_id)
        return BedrockSummarizer(model_id=settings.bedrock_model_id)

    from scheduler.common.summarizer_local import LocalSummarizer

    logger.info("Using LocalSummarizer")
    return LocalSummarizer()
