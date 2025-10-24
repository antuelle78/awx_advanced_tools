# LLM prompt templates

# Template for launching an AWX job template
LAUNCH_JOB_TEMPLATE = (
    "{{\n"
    "  \"template_id\": {template_id},\n"
    "  \"extra_vars\": {extra_vars}\n"
    "}}"
)

# Template for validating a payload against a JSON schema
VALIDATE_SCHEMA_TEMPLATE = (
    "You are given a JSON payload and a JSON schema.\n"
    "Your task is to validate the payload against the schema.\n"
    "If the payload is valid, return: {{\n"
    "  \"valid\": true\n"
    "}}.\n"
    "If the payload is invalid, return: {{\n"
    "  \"valid\": false,\n"
    "  \"errors\": [list of error messages]\n"
    "}}.\n"
)

# Template for summarizing AWX logs
SUMMARIZE_LOG_TEMPLATE = (
    "You are given the following AWX log:\n"
    "{log}\n"
    "Provide a concise summary in JSON format: {{\n"
    "  \"summary\": \u003csummary string\u003e\n"
    "}}.\n"
)
