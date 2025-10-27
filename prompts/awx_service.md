# AWX Service Tool Prompt

## Overview
The AWX Service tool is a Python service class (AWXClient) that handles direct interactions with the Ansible Tower/AWX API. It provides methods for CRUD operations, job management, scheduling, and more. This tool is used internally by the AWX API router to perform actual API calls.

## Key Features
- **Authentication**: Uses username/password from settings for API auth.
- **HTTP Requests**: Asynchronous requests via httpx with error handling.
- **Resource Management**: Methods for users, inventories, projects, organizations, credentials, etc.
- **Job and Workflow Management**: Launch jobs, manage templates, and handle workflows.
- **Notifications and Instance Groups**: Support for notifications and instance group operations.
- **Activity Stream**: Retrieve activity logs.

## Available Methods
- **launch_job_template(template_id: int, extra_vars: dict | None = None)**: Launch a job template.
- **create_inventory(name: str, variables: dict | None = None, organization: int | None = None)**: Create an inventory.
- **get_job(job_id: int)**: Retrieve a job by ID.
- **list_schedules(template_id: int)**: List schedules for a job template.
- **toggle_schedule(schedule_id: int, enabled: bool)**: Enable/disable a schedule.
- **delete_schedule(schedule_id: int)**: Delete a schedule.
- **list_templates(name: Optional[str] = None)**: List all job templates, optionally filtered by name.
- **create_job_template(name: str, inventory: int, project: int, playbook: str, description: Optional[str] = None, extra_vars: Optional[dict] = None)**: Create a job template.
- **list_jobs(page: int = 1)**: List jobs with pagination.
- **get_job(job_id: int)**: Get a job by ID.
- **get_schedule(schedule_id: int)**: Get a schedule by ID.
- **create_schedule(name: str, rrule: str, job_template_id: int)**: Create a schedule.
- **update_schedule(schedule_id: int, name: Optional[str] = None, rrule: Optional[str] = None)**: Update a schedule.
- **delete_schedule(schedule_id: int)**: Delete a schedule.
- **list_inventories(name: Optional[str] = None)**: List all inventories, optionally filtered by name.
- **get_inventory(inventory_id: int)**: Get inventory details.
- **delete_inventory(inventory_id: int)**: Delete an inventory.
- **sync_inventory(inventory_id: int)**: Sync an inventory.
- **list_projects(name: Optional[str] = None)**: List projects, optionally filtered by name.
- **get_project(project_id: int)**: Get a project.
- **create_project(name: str, scm_type: str, scm_url: str, description: Optional[str] = None)**: Create a project.
- **update_project(project_id: int, name: Optional[str] = None, scm_type: Optional[str] = None, scm_url: Optional[str] = None, description: Optional[str] = None)**: Update a project.
- **delete_project(project_id: int)**: Delete a project.
- **sync_project(project_id: int)**: Sync a project.
- **list_organizations(name: Optional[str] = None)**: List organizations, optionally filtered by name.
- **get_organization(organization_id: int)**: Get an organization.
- **create_organization(name: str, description: Optional[str] = None)**: Create an organization.
- **update_organization(organization_id: int, name: Optional[str] = None, description: Optional[str] = None)**: Update an organization.
- **delete_organization(organization_id: int)**: Delete an organization.
- **list_hosts(inventory: Optional[int] = None)**: List all hosts, optionally filtered by inventory.
- **create_host(host_data: dict)**: Create a new host.
- **list_users(username: Optional[str] = None)**: List users, optionally filtered by username.
- **get_user(user_id: int)**: Get a user.
- **get_user_by_name(username: str)**: Get user by username.
- **create_user(username: str, password: str, first_name: Optional[str] = None, last_name: Optional[str] = None, email: Optional[str] = None)**: Create a user.
- **update_user(user_id: int, username: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None, email: Optional[str] = None)**: Update a user.
- **delete_user(user_id: int)**: Delete a user.
- **list_credentials()**: List credentials.
- **get_credential(credential_id: int)**: Get a credential.
- **create_credential(name: str, credential_type: int, inputs: dict)**: Create a credential.
- **update_credential(credential_id: int, name: Optional[str] = None, inputs: Optional[dict] = None)**: Update a credential.
- **delete_credential(credential_id: int)**: Delete a credential.
- **list_workflow_job_templates()**: List workflow job templates.
- **get_workflow_job_template(workflow_job_template_id: int)**: Get a workflow template.
- **create_workflow_job_template(name: str, description: Optional[str] = None)**: Create a workflow template.
- **update_workflow_job_template(workflow_job_template_id: int, name: Optional[str] = None, description: Optional[str] = None)**: Update a workflow template.
- **delete_workflow_job_template(workflow_job_template_id: int)**: Delete a workflow template.
- **launch_workflow_job_template(workflow_job_template_id: int, extra_vars: Optional[dict] = None)**: Launch a workflow template.
- **list_notifications()**: List notification templates.
- **get_notification(notification_id: int)**: Get a notification.
- **create_notification(name: str, notification_type: str, notification_configuration: dict)**: Create a notification.
- **update_notification(notification_id: int, name: Optional[str] = None, notification_configuration: Optional[dict] = None)**: Update a notification.
- **delete_notification(notification_id: int)**: Delete a notification.
- **list_instance_groups()**: List instance groups.
- **get_instance_group(instance_group_id: int)**: Get an instance group.
- **create_instance_group(name: str, policy_instance_percentage: Optional[int] = None, policy_instance_minimum: Optional[int] = None)**: Create an instance group.
- **update_instance_group(instance_group_id: int, name: Optional[str] = None, policy_instance_percentage: Optional[int] = None, policy_instance_minimum: Optional[int] = None)**: Update an instance group.
- **delete_instance_group(instance_group_id: int)**: Delete an instance group.
- **list_activity_stream(page: int = 1, page_size: int = 20)**: List activity stream.

## Usage Examples
- List templates with name filter: `await awx_client.list_templates("my-template")`
- Create job template: `await awx_client.create_job_template("My Job", 1, 2, "playbook.yml")`
- Launch a job: `await awx_client.launch_job_template(123, {"var1": "value"})`
- List hosts in inventory: `await awx_client.list_hosts(5)`
- Create a host: `await awx_client.create_host({"name": "host1", "inventory": 5})`
- List users with filter: `await awx_client.list_users("john")`
- Create a user: `await awx_client.create_user("username", "password", "John", "Doe", "john@example.com")`
- List inventories with name filter: `await awx_client.list_inventories("prod")`
- List jobs: `await awx_client.list_jobs(page=1)`
- Sync a project: `await awx_client.sync_project(456)`
- Create workflow: `await awx_client.create_workflow_job_template("My Workflow")`
- Launch workflow: `await awx_client.launch_workflow_job_template(789, {"vars": "value"})`

## Best Practices
- Ensure AWX_BASE_URL, AWX_USERNAME, and AWX_PASSWORD are set in settings.
- Handle httpx.HTTPStatusError for API errors.
- Use async/await for all method calls.
- Validate parameters to avoid invalid requests.