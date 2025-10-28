# Model capabilities and optimization for different LLM sizes

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ModelCapabilities:
    """Capabilities and limitations of different models."""
    max_tools: int
    context_window: int
    complex_reasoning: bool
    json_accuracy: str  # "low", "medium", "high"
    max_concurrent_tools: int
    supports_multilingual: bool
    recommended_batch_size: int


# Model capabilities database
MODEL_CAPABILITIES: Dict[str, ModelCapabilities] = {
    # Large models (good baseline)
    "gpt-oss:20b": ModelCapabilities(
        max_tools=50,
        context_window=32768,
        complex_reasoning=True,
        json_accuracy="high",
        max_concurrent_tools=5,
        supports_multilingual=True,
        recommended_batch_size=10
    ),

    # Medium models (balanced)
    "granite3.1-dense:8b": ModelCapabilities(
        max_tools=25,
        context_window=131072,
        complex_reasoning=True,
        json_accuracy="high",
        max_concurrent_tools=3,
        supports_multilingual=True,
        recommended_batch_size=8
    ),
    "qwen2.5:7b": ModelCapabilities(
        max_tools=20,
        context_window=32768,
        complex_reasoning=True,
        json_accuracy="high",
        max_concurrent_tools=3,
        supports_multilingual=True,
        recommended_batch_size=6
    ),
    "llama3.1:8b": ModelCapabilities(
        max_tools=20,
        context_window=131072,
        complex_reasoning=True,
        json_accuracy="high",
        max_concurrent_tools=3,
        supports_multilingual=True,
        recommended_batch_size=6
    ),

    # Small models (optimized for efficiency)
    "granite3.1-dense:2b": ModelCapabilities(
        max_tools=10,
        context_window=131072,
        complex_reasoning=False,
        json_accuracy="medium",
        max_concurrent_tools=2,
        supports_multilingual=True,
        recommended_batch_size=4
    ),
    "smollm2:1.7b": ModelCapabilities(
        max_tools=8,
        context_window=8192,
        complex_reasoning=False,
        json_accuracy="medium",
        max_concurrent_tools=1,
        supports_multilingual=False,
        recommended_batch_size=3
    ),
    "qwen2.5:3b": ModelCapabilities(
        max_tools=12,
        context_window=32768,
        complex_reasoning=False,
        json_accuracy="medium",
        max_concurrent_tools=2,
        supports_multilingual=True,
        recommended_batch_size=4
    ),
    "hermes3:3b": ModelCapabilities(
        max_tools=15,
        context_window=131072,
        complex_reasoning=True,
        json_accuracy="high",
        max_concurrent_tools=2,
        supports_multilingual=False,
        recommended_batch_size=5
    ),

    # Very small models (minimal functionality)
    "smollm2:360m": ModelCapabilities(
        max_tools=5,
        context_window=8192,
        complex_reasoning=False,
        json_accuracy="low",
        max_concurrent_tools=1,
        supports_multilingual=False,
        recommended_batch_size=2
    ),
    "smollm2:135m": ModelCapabilities(
        max_tools=3,
        context_window=8192,
        complex_reasoning=False,
        json_accuracy="low",
        max_concurrent_tools=1,
        supports_multilingual=False,
        recommended_batch_size=1
    )
}


# Tool groupings for progressive exposure
TOOL_GROUPS = {
    "basic": [
        "list_templates", "launch_job_template", "get_job", "list_jobs",
        "health_check", "test_connection"
    ],
    "inventory": [
        "list_inventories", "get_inventory", "create_inventory",
        "sync_inventory", "delete_inventory"
    ],
    "users": [
        "list_users", "get_user", "get_user_by_name", "create_user",
        "update_user", "delete_user"
    ],
    "projects": [
        "list_projects", "get_project", "create_project", "update_project",
        "sync_project", "delete_project"
    ],
    "organizations": [
        "list_organizations", "get_organization", "create_organization",
        "update_organization", "delete_organization"
    ],
    "schedules": [
        "list_schedules", "get_schedule", "create_schedule",
        "update_schedule", "delete_schedule"
    ],
    "advanced": [
        "create_job_template", "list_hosts", "create_host",
        "list_credentials", "create_credential", "update_credential", "delete_credential",
        "list_workflow_job_templates", "create_workflow_job_template",
        "launch_workflow_job_template", "update_workflow_job_template", "delete_workflow_job_template",
        "list_notifications", "create_notification", "update_notification", "delete_notification",
        "list_instance_groups", "create_instance_group", "update_instance_group", "delete_instance_group",
        "list_activity_stream"
    ]
}


# Complex tools that require advanced reasoning
COMPLEX_TOOLS = [
    "create_job_template", "create_workflow_job_template",
    "launch_workflow_job_template", "create_credential",
    "create_notification", "create_instance_group"
]


def get_model_capabilities(model_name: str) -> ModelCapabilities:
    """Get capabilities for a specific model."""
    # Try exact match first
    if model_name in MODEL_CAPABILITIES:
        return MODEL_CAPABILITIES[model_name]

    # Try partial matches (e.g., "granite3.1-dense" matches "granite3.1-dense:2b")
    for known_model, capabilities in MODEL_CAPABILITIES.items():
        if known_model.split(':')[0] in model_name:
            return capabilities

    # Default to conservative settings
    return ModelCapabilities(
        max_tools=10,
        context_window=8192,
        complex_reasoning=False,
        json_accuracy="medium",
        max_concurrent_tools=2,
        supports_multilingual=False,
        recommended_batch_size=3
    )


def get_available_tools(model_name: str, conversation_length: int = 0) -> List[str]:
    """Get available tools based on model capabilities and conversation context."""
    capabilities = get_model_capabilities(model_name)

    # Start with basic tools
    available_tools = TOOL_GROUPS["basic"].copy()

    # Add inventory tools after some conversation
    if conversation_length >= 1:
        available_tools.extend(TOOL_GROUPS["inventory"])

    # Add user management tools
    if capabilities.max_tools >= 8:
        available_tools.extend(TOOL_GROUPS["users"])

    # Add project/organization tools for capable models
    if capabilities.max_tools >= 12:
        available_tools.extend(TOOL_GROUPS["projects"])
        available_tools.extend(TOOL_GROUPS["organizations"])

    # Add scheduling for models with good reasoning
    if capabilities.complex_reasoning and capabilities.max_tools >= 15:
        available_tools.extend(TOOL_GROUPS["schedules"])

    # Add advanced tools only for capable models
    if capabilities.max_tools >= 20 and capabilities.complex_reasoning:
        available_tools.extend(TOOL_GROUPS["advanced"])

    # Limit to model's max_tools capacity
    return available_tools[:capabilities.max_tools]


def should_use_simplified_prompt(model_name: str, tool_name: str) -> bool:
    """Determine if a simplified prompt should be used."""
    capabilities = get_model_capabilities(model_name)

    # Use simplified prompts for smaller models or complex tools
    if capabilities.max_tools <= 10:
        return True

    if tool_name in COMPLEX_TOOLS and not capabilities.complex_reasoning:
        return True

    return False


def get_context_limits(model_name: str) -> Dict[str, int]:
    """Get context management limits for a model."""
    capabilities = get_model_capabilities(model_name)

    return {
        "max_context_items": min(10, capabilities.recommended_batch_size * 2),
        "context_summary_trigger": capabilities.recommended_batch_size * 3,
        "max_tool_calls_per_response": capabilities.max_concurrent_tools
    }


def is_model_suitable_for_complex_tasks(model_name: str) -> bool:
    """Check if model is suitable for complex AWX administration tasks."""
    capabilities = get_model_capabilities(model_name)
    return (capabilities.max_tools >= 15 and
            capabilities.complex_reasoning and
            capabilities.context_window >= 32768)