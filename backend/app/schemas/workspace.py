from datetime import date, timedelta
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ActionInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=3, max_length=200)
    owner: str = Field(min_length=2, max_length=100)
    due_date: date
    timezone: str = "UTC"
    renewal_date: date | None = None
    notice_days: int | None = Field(default=None, ge=0, le=730)
    notes: str = Field(default="", max_length=3000)
    confirmed: Literal[True]

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value):
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError("Choose a valid IANA time zone")
        return value

    @model_validator(mode="after")
    def check_notice_date(self):
        if (self.renewal_date is None) != (self.notice_days is None):
            raise ValueError("Supply both renewal date and calendar-day notice period")
        if self.renewal_date and self.due_date != self.renewal_date - timedelta(days=self.notice_days):
            raise ValueError("Notice deadline must equal renewal date minus calendar-day notice period")
        return self


class ActionCreate(ActionInput):
    document_id: str
    analysis_id: str | None = None
    deadline_id: str | None = None

    @model_validator(mode="after")
    def source_pair(self):
        if bool(self.analysis_id) != bool(self.deadline_id):
            raise ValueError("Select both a source analysis and deadline")
        return self


class ActionEdit(ActionInput):
    version: int = Field(ge=1)


class StatusChange(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    version: int = Field(ge=1)
    status: Literal["open", "completed", "cancelled"]
    note: str = Field(min_length=5, max_length=3000)
