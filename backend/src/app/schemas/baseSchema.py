from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator

from app.core.sanitizer import sanitizeAnyValue


class SanitizedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Dibantu AI: sanitizeValues
    @model_validator(mode="before")
    @classmethod
    def sanitizeValues(cls, inputValue: Any) -> Any:
        if isinstance(inputValue, dict):
            try:
                return sanitizeAnyValue(inputValue)
            except ValueError as errorValue:
                raise ValueError(str(errorValue)) from errorValue
        return inputValue
