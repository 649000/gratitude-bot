import logging

logger = logging.getLogger(__name__)

_cache: dict[str, str | None] = {}


def get_parameter(name: str, decrypt: bool = True) -> str | None:
    if name in _cache:
        return _cache[name]

    try:
        import boto3
        from botocore.exceptions import ClientError

        ssm = boto3.client("ssm")
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


def load_parameters(env: str, path: str = "/gratitude-bot") -> dict[str, str]:
    full_path = f"{path}/{env}"
    params: dict[str, str] = {}

    try:
        import boto3
        from botocore.exceptions import ClientError

        ssm = boto3.client("ssm")
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
