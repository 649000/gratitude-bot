import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

_cache: dict[str, str | None] = {}


def _default_ssm_client() -> Any:
    import boto3

    return boto3.client("ssm")


def get_parameter(
    name: str,
    decrypt: bool = True,
    *,
    client_factory: Callable[[], Any] = _default_ssm_client,
) -> str | None:
    if name in _cache:
        return _cache[name]

    try:
        from botocore.exceptions import ClientError

        ssm = client_factory()
        response = ssm.get_parameter(Name=name, WithDecryption=decrypt)
        value = response["Parameter"]["Value"]
        _cache[name] = value
        return value
    except ImportError:
        logger.debug("boto3 not available — skipping SSM")
        _cache[name] = None
    except ClientError as e:
        logger.warning("SSM parameter %s not found: %s", name, e)
        _cache[name] = None
    except Exception as e:
        logger.warning("SSM lookup failed for %s: %s", name, e)
        _cache[name] = None

    return None


def load_parameters(
    env: str,
    path: str = "/gratitude-bot",
    *,
    client_factory: Callable[[], Any] = _default_ssm_client,
) -> dict[str, str]:
    full_path = f"{path}/{env}"
    params: dict[str, str] = {}

    try:
        from botocore.exceptions import ClientError

        ssm = client_factory()
        paginator = ssm.get_paginator("get_parameters_by_path")

        for page in paginator.paginate(
            Path=full_path,
            Recursive=True,
            WithDecryption=True,
        ):
            for p in page["Parameters"]:
                key = p["Name"].split("/")[-1]
                params[key] = p["Value"]

        if not params:
            logger.warning("No parameters found at SSM path %s", full_path)
        else:
            logger.info("Loaded %d parameters from SSM path %s", len(params), full_path)
    except ImportError:
        logger.debug("boto3 not available — skipping SSM bulk load")
    except ClientError as e:
        logger.warning("SSM path %s not accessible: %s", full_path, e)
    except Exception as e:
        logger.warning("SSM bulk load failed for %s: %s", full_path, e)

    return params


def clear_cache() -> None:
    _cache.clear()
