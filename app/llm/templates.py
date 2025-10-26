# LLM prompt templates with standardized instructions and output format

# Template for launching an AWX job template
LAUNCH_JOB_TEMPLATE = (
    "You are given a template_id and extra_vars.\n"
    "Think step-by-step: first ensure template_id is a positive integer, then embed extra_vars as a JSON object.\n"
    "Only return a JSON object in the format {{\"result\": {{\"template_id\": {template_id}, \"extra_vars\": {extra_vars}}}}}, no markdown or explanations."
)

# Template for validating a payload against a JSON schema
VALIDATE_SCHEMA_TEMPLATE = (
    "You are given a JSON payload and a JSON schema.\n"
    "Think step-by-step: first identify missing required fields, then check field types, and finally ensure no additional properties are present.\n"
    "Only return a JSON object in the format {{\"result\": {{\"valid\": true}}}} if valid, or {{\"result\": {{\"valid\": false, \"errors\": [list of error messages]}}}} if invalid, no markdown or explanations."
)

# Template for summarizing AWX logs
SUMMARIZE_LOG_TEMPLATE = (
    "You are given the following AWX log:\n{log}\n"
    "Think step-by-step: summarize the key events and outcomes in 80 words.\n"
    "Only return a JSON object in the format {{\"result\": {{\"summary\": \"<concise summary>\"}}}}, no markdown or explanations."
)

GET_AWX_STATUS_TEMPLATE = (
    "You are given AWX instance URL and credentials.\n"
    "Think step-by-step: perform a GET request to '/api/v2/status/' and extract the status code and body.\n"
    "Only return a JSON object in the format {{\"result\": {{\"code\": <int>, \"body\": \"<string>\"}}}}, no markdown or explanations."
)

CREATE_PROJECT_TEMPLATE = (
    "You are given AWX instance information, a project name, and a JWT token.\n"
    "Think step-by-step: POST to '/api/v2/projects/' with the required JSON body.\n"
    "Only return a JSON object in the format {{\"result\": <AWX response JSON>}}, no markdown or explanations."
)

TEMPLATES = {
    "launch_job_template": LAUNCH_JOB_TEMPLATE,
    "validate_schema": VALIDATE_SCHEMA_TEMPLATE,
    "summarize_log": SUMMARIZE_LOG_TEMPLATE,
    "get_awx_status": GET_AWX_STATUS_TEMPLATE,
    "create_project": CREATE_PROJECT_TEMPLATE,
}


