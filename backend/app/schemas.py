"""Request/response schemas (Pydantic v2)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from .config import MAX_TEXT_LENGTH


class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty.")
        return value

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, value: str, info):
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Passwords do not match.")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class PredictionRequest(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TEXT_LENGTH)


class ClassScore(BaseModel):
    label: str
    score: float


class PredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    label: str
    confidence: float | None = None
    score_type: str = "probability"
    scores: list[ClassScore] | None = None
    model_name: str
    created_at: datetime


class PredictionList(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[PredictionOut]


class CategoryCount(BaseModel):
    label: str
    count: int


class DashboardStats(BaseModel):
    total_predictions: int
    counts_by_label: list[CategoryCount]
    recent: list[PredictionOut]
    model_name: str
    model_accuracy_test: float | None = None


class HealthOut(BaseModel):
    status: str
    model_ready: bool
    model_name: str | None = None
    detail: str | None = None
