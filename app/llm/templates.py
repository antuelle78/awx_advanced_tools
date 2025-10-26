# LLM prompt templates

# Template for launching an AWX job template with strict JSON output
# Template for launching an AWX job template with chain‑of‑thought examples and strict format
LAUNCH_JOB_TEMPLATE = (
    '{{\n  "template_id": {template_id},\n  "extra_vars": {extra_vars}\n}}\n\nThink step‑by‑step: first ensure template_id is a positive integer, then embed extra_vars as a JSON object.\n\nOnly return the JSON object, no markdown or explanations.'
)

# Template for validating a payload against a JSON schema
# Template for validating a payload against a JSON schema with chain‑of‑thought examples
VALIDATE_SCHEMA_TEMPLATE = (
    "You are given a JSON payload and a JSON schema.\n" \
    "Your task is to validate the payload against the schema.\n" \
    "Return the validation result as \n{\n  \"valid\": true\n} if valid, or \n{\n  \"valid\": false,\n  \"errors\": [list of error messages]\n} if invalid.\n\nThink step‑by‑step: first identify missing required fields, then check field types, and finally ensure no additional properties are present.\n\nOnly return the JSON object, no markdown or explanations."
)

# Template for summarizing AWX logs
# Template for summarizing AWX logs with chain‑of‑thought and strict JSON
SUMMARIZE_LOG_TEMPLATE = (
    "You are given the following AWX log:\n" \
    "{log}\n" \
    "Provide a concise summary in JSON format.\n" \
    "Summarize to 80 words.\n" \
    "Only return the JSON object, no markdown or explanations."
)

GET_AWX_STATUS_TEMPLATE = (
    "You are given AWX instance URL and credentials.\n"
    "Your task is to perform a GET request to '/api/v2/status/' and provide the HTTP status code and body as a JSON object.\n"
    "Return {\n  \"code\": <int>,\n  \"body\": <string>\n} and do not return markdown.\n"
    "Only return the JSON object, no markdown or explanations."

)

CREATE_PROJECT_TEMPLATE = (
    "You are given AWX instance information, a project name, and a JWT token.\n"
    "Your task is to POST to '/api/v2/projects/' with a strict JSON body containing name=\'{project_name}\', organization=1, scm_type=\'git\', scm_url=repo_url.\n"
    "Return the AWX project creation response as a JSON object.\n"
    "Only return the JSON object, no markdown."
)

TEMPLATES = {
    "launch_job_template": LAUNCH_JOB_TEMPLATE,
    "validate_schema": VALIDATE_SCHEMA_TEMPLATE,
    "summarize_log": SUMMARIZE_LOG_TEMPLATE,
    "get_awx_status": GET_AWX_STATUS_TEMPLATE,
    "create_project": CREATE_PROJECT_TEMPLATE,
}


