from datetime import UTC, datetime

app_start_time: datetime | None = None


def set_start_time() -> None:
    global app_start_time
    app_start_time = datetime.now(UTC)
