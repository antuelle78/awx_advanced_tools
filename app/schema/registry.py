from typing import Dict

# Example registry mapping platform and action to JSON schema
schema_registry: Dict[str, Dict[str, Dict]] = {
    "generic": {
        "mcp": {
            "type": "object",
            "properties": {
                "context_id": {"type": ["string", "null"]},
                "platform": {"type": "string"},
                "action": {"type": "string"},
                "payload": {"type": "object"},
            },
            "required": ["platform", "action", "payload"],
            "additionalProperties": False,
        }
    },
    "AWX": {
        "create_ticket": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["title", "description"],
            "additionalProperties": False,
        }
    },
}

# Function to retrieve schema


def get_schema(platform: str, action: str):
    return schema_registry.get(platform, {}).get(action)
