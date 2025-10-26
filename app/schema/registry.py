from typing import Dict

# Registry mapping platform and action to JSON schema for LLM output validation
schema_registry: Dict[str, Dict[str, Dict]] = {
    "AWX": {
        "launch_job_template": {
            "type": "object",
            "properties": {
                "result": {
                    "type": "object",
                    "properties": {
                        "template_id": {"type": "integer"},
                        "extra_vars": {"type": "object"},
                    },
                    "required": ["template_id", "extra_vars"],
                    "additionalProperties": False,
                }
            },
            "required": ["result"],
            "additionalProperties": False,
        },
        "validate_schema": {
            "type": "object",
            "properties": {
                "result": {
                    "type": "object",
                    "properties": {
                        "valid": {"type": "boolean"},
                        "errors": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["valid"],
                    "additionalProperties": False,
                }
            },
            "required": ["result"],
            "additionalProperties": False,
        },
        "summarize_log": {
            "type": "object",
            "properties": {
                "result": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                    },
                    "required": ["summary"],
                    "additionalProperties": False,
                }
            },
            "required": ["result"],
            "additionalProperties": False,
        },
        "get_awx_status": {
            "type": "object",
            "properties": {
                "result": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "integer"},
                        "body": {"type": "string"},
                    },
                    "required": ["code", "body"],
                    "additionalProperties": False,
                }
            },
            "required": ["result"],
            "additionalProperties": False,
        },
        "create_project": {
            "type": "object",
            "properties": {
                "result": {"type": "object"},  # Variable AWX response
            },
            "required": ["result"],
            "additionalProperties": False,
        },
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
