# LLM prompt templates with standardized instructions and output format

# Template for launching an AWX job template
LAUNCH_JOB_TEMPLATE = (
    "You are given a template_id and extra_vars.\n"
    "Think step-by-step: first ensure template_id is a positive integer, then embed extra_vars as a JSON object.\n"
    'Always format your response as a markdown table showing the operation result. Use columns: Operation, Status, Details.'
)

# Template for validating a payload against a JSON schema
VALIDATE_SCHEMA_TEMPLATE = (
    "You are given a JSON payload and a JSON schema.\n"
    "Think step-by-step: first identify missing required fields, then check field types, and finally ensure no additional properties are present.\n"
    'Always format your response as a markdown table showing validation results. Use columns: Validation, Status, Details.'
)

# Template for summarizing AWX logs
SUMMARIZE_LOG_TEMPLATE = (
    "You are given the following AWX log:\n{log}\n"
    "Think step-by-step: summarize the key events and outcomes in 80 words.\n"
    'Always format your response as a markdown table showing the summary. Use columns: Summary Type, Content.'
)

GET_AWX_STATUS_TEMPLATE = (
    "You are given AWX instance URL and credentials.\n"
    "Think step-by-step: perform a GET request to '/api/v2/status/' and extract the status code and body.\n"
    'Always format your response as a markdown table showing the status. Use columns: Status Code, Response Body.'
)

CREATE_PROJECT_TEMPLATE = (
    "You are given AWX instance information, a project name, and a JWT token.\n"
    "Think step-by-step: POST to '/api/v2/projects/' with the required JSON body.\n"
    'Always format your response as a markdown table showing the creation result. Use columns: Operation, Status, Project Details.'
)

CREATE_HOST_TEMPLATE = (
    "You are given host data including name and inventory.\n"
    "Think step-by-step: Validate the data, then POST to '/api/v2/hosts/'.\n"
    'Always format your response as a markdown table showing the creation result. Use columns: Operation, Status, Host Details.'
)

CREATE_JOB_TEMPLATE_TEMPLATE = (
    "You are given job template data including name, inventory, project, playbook.\n"
    "Think step-by-step: Validate the data, then POST to '/api/v2/job_templates/'.\n"
    'Always format your response as a markdown table showing the creation result. Use columns: Operation, Status, Template Details.'
)

TEMPLATES = {
    "launch_job_template": LAUNCH_JOB_TEMPLATE,
    "validate_schema": VALIDATE_SCHEMA_TEMPLATE,
    "summarize_log": SUMMARIZE_LOG_TEMPLATE,
    "get_awx_status": GET_AWX_STATUS_TEMPLATE,
    "create_project": CREATE_PROJECT_TEMPLATE,
    "create_host": CREATE_HOST_TEMPLATE,
    "create_job_template": CREATE_JOB_TEMPLATE_TEMPLATE,
}
