from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class AnalysisRequest(BaseModel):
    repository: str = Field(examples=["fastapi/fastapi"])

    @field_validator("repository")
    @classmethod
    def normalize_repository(cls, value: str) -> str:
        return value.strip()


class ActionItemRequest(BaseModel):
    repository: str = Field(min_length=3, max_length=200)
    title: str = Field(min_length=3, max_length=240)
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
