"""Explicit direct-PII policy for application and event boundaries."""

from typing import Any

DIRECT_PII_KEYS = frozenset(
    {
        "email",
        "email_address",
        "phone",
        "phone_number",
        "full_name",
        "first_name",
        "last_name",
        "street_address",
        "home_address",
        "ssn",
        "social_security_number",
        "card_number",
        "cvv",
        "bank_account",
        "routing_number",
    }
)


def direct_pii_paths(value: Any, prefix: str = "") -> list[str]:
    """Return dotted paths whose key names are classified as direct PII."""
    matches: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            if key_text.lower() in DIRECT_PII_KEYS:
                matches.append(path)
            matches.extend(direct_pii_paths(nested, path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            path = f"{prefix}[{index}]" if prefix else f"[{index}]"
            matches.extend(direct_pii_paths(nested, path))
    return matches


def assert_no_direct_pii(value: Any) -> None:
    """Reject payloads containing direct-identifier fields at the event boundary."""
    paths = direct_pii_paths(value)
    if paths:
        raise ValueError(f"Direct PII fields are not allowed in event payloads: {', '.join(paths)}")
