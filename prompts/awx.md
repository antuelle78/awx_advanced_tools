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
- To list job templates with name filter: GET /awx/templates?name=my-template
- To create a job template: POST /awx/job_templates with name, inventory, project, playbook, etc.
- To launch a job template: POST /awx/job_templates/123/launch with optional extra_vars JSON.
- To list hosts in an inventory: GET /awx/hosts?inventory=5
- To create a host: POST /awx/hosts with name, inventory, and optional variables.
- To list users with username filter: GET /awx/users?username=john
- To create a user: POST /awx/users with username, password, and optional fields like first_name, last_name, email.
- To list inventories with name filter: GET /awx/inventories?name=my-inventory
- To create a schedule: POST /awx/job_templates/123/schedules with name, rrule, and job_template_id.
- To manage credentials: Use GET/POST/PATCH/DELETE /awx/credentials endpoints.
- To work with workflows: Use /awx/workflow_job_templates endpoints for creation and launching.
- To set up notifications: Use /awx/notification_templates endpoints.
- To manage instance groups: Use /awx/instance_groups endpoints for scaling.
- To monitor activity: GET /awx/activity_stream?page=1&page_size=20

## Best Practices
- Ensure AWX credentials are configured in settings.
- Handle HTTP errors (e.g., 400 for bad requests, 404 for not found).
- Use pagination for large lists (e.g., jobs).
- Validate inputs to prevent errors.