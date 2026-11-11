from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MonitorCheckRead(BaseModel):
    id: int
    monitor_id: int
    status_code: int | None
    response_time_ms: float | None
    is_available: bool
    error_message: str | None
    checked_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MonitorStatus(BaseModel):
    monitor_id: int
    is_active: bool
    last_check: MonitorCheckRead | None
