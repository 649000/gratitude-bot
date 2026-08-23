from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from scheduler.common.config import settings
from scheduler.common.database import async_session_factory

logger = Logger(service="dispatcher")


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    import asyncio

    from scheduler.dispatcher.dispatch import handle_dispatch

    queue_url = settings.sqs_queue_url

    async def main():
        try:
            return await handle_dispatch(queue_url)
        finally:
            await async_session_factory.dispose()

    return asyncio.run(main())
