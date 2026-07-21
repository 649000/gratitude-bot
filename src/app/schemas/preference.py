import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserPreferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    digest_weekly_enabled: bool = True
    digest_monthly_enabled: bool = True
    digest_yearly_enabled: bool = True
    rediscovery_enabled: bool = True
    reminder_enabled: bool = True
    last_rediscovery_at: datetime | None = None
    onboarding_completed: bool = False


class UserPreferenceUpdate(BaseModel):
    digest_weekly_enabled: bool | None = None
    digest_monthly_enabled: bool | None = None
    digest_yearly_enabled: bool | None = None
    rediscovery_enabled: bool | None = None
    reminder_enabled: bool | None = None
    onboarding_completed: bool | None = None
