import asyncio
import json

from aws_lambda_powertools.utilities.typing import LambdaContext
from mangum import Mangum

from app.logging_config import get_logger
from app.main import app

logger = get_logger()

_mangum = Mangum(app, lifespan="auto")
_loop: asyncio.AbstractEventLoop | None = None


def _get_or_create_loop() -> asyncio.AbstractEventLoop:
    global _loop
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    return _loop


def _is_sqs_event(event: dict) -> bool:
    if not isinstance(event, dict):
        return False
    records = event.get("Records", [])
    if records and len(records) > 0:
        return records[0].get("eventSource") == "aws:sqs"
    return False


@logger.inject_lambda_context(log_event=True)
def handler(event: dict, context: LambdaContext):
    if _is_sqs_event(event):
        return _handle_sqs(event, context)

    return _mangum(event, context)


def _handle_sqs(event: dict, _context: object) -> dict:
    from app.telegram.sqs_handler import handle_sqs_records

    records = event.get("Records", [])
    try:
        loop = _get_or_create_loop()
        result = loop.run_until_complete(handle_sqs_records(records))
        logger.info("SQS batch processed: %s", json.dumps(result))
        return result
    except Exception:
        logger.exception("SQS batch handler crashed")
        return {"status": "error", "records_processed": 0}
