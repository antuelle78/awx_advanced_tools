# Add a simple JSON schema validator that uses jsonschema
from typing import Dict
from jsonschema import validate

# Registry of schemas per platform/action
from app.schema.registry import schema_registry

# Helper to get schema for a platform and action


def get_schema(platform: str, action: str) -> Dict | None:
    return schema_registry.get(platform, {}).get(action)


# Validate a payload against a schema


def validate_payload(platform: str, action: str, payload: Dict) -> None:
    schema = get_schema(platform, action)
    if schema is None:
        raise ValueError(f"No schema found for {platform}/{action}")
    validate(instance=payload, schema=schema)
