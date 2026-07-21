import json
import logging

from scheduler.common.config import settings

logger = logging.getLogger(__name__)


def lambda_handler(event: dict, _context: object) -> dict:
    logger.info("Received event: %s", json.dumps(event))

    import asyncio

    from scheduler.dispatcher.dispatch import handle_dispatch

    queue_url = settings.sqs_queue_url
    result = asyncio.run(handle_dispatch(queue_url))
    return result
