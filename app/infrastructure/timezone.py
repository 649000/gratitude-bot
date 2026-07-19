import logging

import httpx

logger = logging.getLogger(__name__)

_TIMEZONE_API_URL = "https://timeapi.io/api/TimeZone/coordinate"


async def get_timezone(lat: float, lng: float) -> str | None:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                _TIMEZONE_API_URL,
                params={"latitude": lat, "longitude": lng},
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
            tz = data.get("timeZone")
            if tz:
                return tz
    except httpx.HTTPStatusError:
        logger.warning("Timezone API returned error for %s, %s", lat, lng)
    except httpx.RequestError:
        logger.warning("Timezone API request failed for %s, %s", lat, lng)
    except Exception:
        logger.warning("Timezone API unexpected error for %s, %s", lat, lng)

    return None
