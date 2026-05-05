from __future__ import annotations

import html
from typing import Any

blockedFragments = ["<script", "</script", "javascript:", "onerror=", "onload="]


# Dibantu AI: sanitizeStringValue
def sanitizeStringValue(rawValue: str) -> str:
    normalizedValue = html.escape(rawValue.strip(), quote=True)
    loweredValue = normalizedValue.lower()
    for blockedFragment in blockedFragments:
        if blockedFragment in loweredValue:
            raise ValueError("Blocked string content")
    return normalizedValue


# Dibantu AI: sanitizeAnyValue
def sanitizeAnyValue(rawValue: Any) -> Any:
    if isinstance(rawValue, str):
        return sanitizeStringValue(rawValue)

    if isinstance(rawValue, list):
        return [sanitizeAnyValue(itemValue) for itemValue in rawValue]

    if isinstance(rawValue, dict):
        return {
            sanitizeStringValue(keyValue) if isinstance(keyValue, str) else keyValue: sanitizeAnyValue(
                itemValue
            )
            for keyValue, itemValue in rawValue.items()
        }

    return rawValue
