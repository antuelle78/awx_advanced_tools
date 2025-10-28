# AWX Tool Prompt

## Overview
The AWX tool is a FastAPI-based API router that provides endpoints for interacting with Ansible Tower/AWX. It handles operations such as launching job templates, managing users, inventories, projects, organizations, schedules, and more. This tool is designed for automation and orchestration tasks in an AWX environment.

## Key Features
- **Job Management**: Launch job templates, list jobs, and manage schedules.
- **Resource Management**: Create, read, update, delete (CRUD) operations for users, inventories, projects, organizations, and credentials.
- **Scheduling**: Create and manage schedules for job templates.
- **Error Handling**: Uses HTTP exceptions for client errors and custom exceptions for internal logic.

## Available Endpoints
- **GET /awx/templates**: List job templates (optional name filter).
- **POST /awx/job_templates/{template_id}/launch**: Launch a job template with optional extra variables.
- **GET /awx/jobs**: List jobs with pagination.
- **GET /awx/jobs/{job_id}**: Get a specific job.
- **POST /awx/job_templates**: Create a new job template.
- **GET /awx/inventories**: List inventories (optional name filter).
- **POST /awx/inventories**: Create a new inventory.
- **GET /awx/inventories/{inventory_id}**: Get an inventory.
- **DELETE /awx/inventories/{inventory_id}**: Delete an inventory.
- **POST /awx/inventories/{inventory_id}/sync**: Sync an inventory.
- **GET /awx/projects**: List projects (optional name filter).
- **GET /awx/projects/{project_id}**: Get a project.
- **POST /awx/projects**: Create a project.
- **PATCH /awx/projects/{project_id}**: Update a project.
- **DELETE /awx/projects/{project_id}**: Delete a project.
- **POST /awx/projects/{project_id}/sync**: Sync a project.
- **GET /awx/organizations**: List organizations (optional name filter).
- **GET /awx/organizations/{organization_id}**: Get an organization.
- **POST /awx/organizations**: Create an organization.
- **PATCH /awx/organizations/{organization_id}**: Update an organization.
- **DELETE /awx/organizations/{organization_id}**: Delete an organization.
- **GET /awx/hosts**: List hosts (optional inventory filter).
- **POST /awx/hosts**: Create a new host.
- **GET /awx/users**: List users (optional username filter).
- **GET /awx/users/{user_id}**: Get a specific user.
- **GET /awx/users/by-name/{username}**: Get user by username.
- **POST /awx/users**: Create a new user.
- **PATCH /awx/users/{user_id}**: Update a user.
- **DELETE /awx/users/{user_id}**: Delete a user.
- **GET /awx/job_templates/{template_id}/schedules**: List schedules for a template.
- **GET /awx/schedules/{schedule_id}**: Get a schedule.
- **POST /awx/job_templates/{template_id}/schedules**: Create a schedule.
- **PATCH /awx/schedules/{schedule_id}**: Update a schedule.
- **DELETE /awx/schedules/{schedule_id}**: Delete a schedule.
- **GET /awx/credentials**: List credentials.
- **GET /awx/credentials/{credential_id}**: Get a credential.
- **POST /awx/credentials**: Create a credential.
- **PATCH /awx/credentials/{credential_id}**: Update a credential.
- **DELETE /awx/credentials/{credential_id}**: Delete a credential.
- **GET /awx/workflow_job_templates**: List workflow job templates.
- **GET /awx/workflow_job_templates/{workflow_job_template_id}**: Get a workflow template.
- **POST /awx/workflow_job_templates**: Create a workflow template.
- **PATCH /awx/workflow_job_templates/{workflow_job_template_id}**: Update a workflow template.
- **DELETE /awx/workflow_job_templates/{workflow_job_template_id}**: Delete a workflow template.
- **POST /awx/workflow_job_templates/{workflow_job_template_id}/launch**: Launch a workflow template.
- **GET /awx/notification_templates**: List notification templates.
- **GET /awx/notification_templates/{notification_id}**: Get a notification.
- **POST /awx/notification_templates**: Create a notification.
- **PATCH /awx/notification_templates/{notification_id}**: Update a notification.
- **DELETE /awx/notification_templates/{notification_id}**: Delete a notification.
- **GET /awx/instance_groups**: List instance groups.
- **GET /awx/instance_groups/{instance_group_id}**: Get an instance group.
- **POST /awx/instance_groups**: Create an instance group.
- **PATCH /awx/instance_groups/{instance_group_id}**: Update an instance group.
- **DELETE /awx/instance_groups/{instance_group_id}**: Delete an instance group.
- **GET /awx/activity_stream**: List activity stream with pagination.

## Usage Examples
- To list job templates with name filter: Use list_templates(name='my-template')
- To create a job template: Use create_job_template(name='My Job', inventory=1, project=2, playbook='playbook.yml')
- To launch a job template: Use launch_job_template(template_id=123, extra_vars={'var': 'value'})
- To list hosts in an inventory: Use list_hosts(inventory=5)
- To create a host: Use create_host(host_data={'name': 'host1', 'inventory': 5})
- To list users with username filter: Use list_users(username='john')
- To create a user: Use create_user(username='user', password='pass', first_name='John', last_name='Doe', email='john@example.com')
- To list inventories with name filter: Use list_inventories(name='my-inventory')
- To create a schedule: Use create_schedule(name='Daily Backup', rrule='FREQ=DAILY', job_template_id=123)
- To manage credentials: Use list_credentials(), create_credential(), etc.
- To work with workflows: Use list_workflow_job_templates(), launch_workflow_job_template()
- To set up notifications: Use list_notifications(), create_notification()
- To manage instance groups: Use list_instance_groups(), create_instance_group()
- To monitor activity: Use list_activity_stream(page=1, page_size=20)

## Best Practices
- Ensure AWX credentials are configured in settings.
- Handle HTTP errors (e.g., 400 for bad requests, 404 for not found).
- Use pagination for large lists (e.g., jobs).
- Validate inputs to prevent errors.