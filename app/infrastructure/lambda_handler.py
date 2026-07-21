import json
import logging

from mangum import Mangum

from app.main import app

logger = logging.getLogger(__name__)

_mangum = Mangum(app, lifespan="auto")
_initialized = False


def _is_sqs_event(event: dict) -> bool:
    if not isinstance(event, dict):
        return False
    records = event.get("Records", [])
    if records and len(records) > 0:
        return records[0].get("eventSource") == "aws:sqs"
    return False


def handler(event: dict, context: object):
    if _is_sqs_event(event):
        return _handle_sqs(event, context)

    return _mangum(event, context)


def _handle_sqs(event: dict, _context: object) -> dict:
    from app.logging_config import configure_logging

    global _initialized
    if not _initialized:
        configure_logging()
        _initialized = True

    import asyncio

    from app.telegram.sqs_handler import handle_sqs_records

    records = event.get("Records", [])
    result = asyncio.run(handle_sqs_records(records))
    logger.info("SQS batch processed: %s", json.dumps(result))
    return result
