from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class MonitorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    url: HttpUrl
    description: str | None = Field(default=None, max_length=2000)
    is_active: bool = True
    check_interval: int = Field(default=300, ge=30, le=86400)

    @field_validator("url")
    @classmethod
    def only_http_schemes(cls, value: HttpUrl) -> HttpUrl:
        if value.scheme not in {"http", "https"}:
            raise ValueError("Only HTTP and HTTPS URLs are supported")
        return value


class MonitorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    url: HttpUrl | None = None
    description: str | None = Field(default=None, max_length=2000)
    is_active: bool | None = None
    check_interval: int | None = Field(default=None, ge=30, le=86400)


class MonitorRead(BaseModel):
    id: int
    name: str
    url: str
    description: str | None
    is_active: bool
    check_interval: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
