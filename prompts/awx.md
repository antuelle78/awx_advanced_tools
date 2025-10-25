# AWX Tool Prompt

## Overview
The AWX tool is a FastAPI-based API router that provides endpoints for interacting with Ansible Tower/AWX. It handles operations such as launching job templates, managing users, inventories, projects, organizations, schedules, and more. This tool is designed for automation and orchestration tasks in an AWX environment.

## Key Features
- **Job Management**: Launch job templates, list jobs, and manage schedules.
- **Resource Management**: Create, read, update, delete (CRUD) operations for users, inventories, projects, organizations, and credentials.
- **Scheduling**: Create and manage schedules for job templates.
- **Error Handling**: Uses HTTP exceptions for client errors and custom exceptions for internal logic.

## Available Endpoints
- **POST /awx/job_templates/{template_id}/launch**: Launch a job template with optional extra variables.
- **GET /awx/users**: List all users.
- **GET /awx/users/{user_id}**: Get a specific user.
- **POST /awx/users**: Create a new user.
- **PATCH /awx/users/{user_id}**: Update a user.
- **DELETE /awx/users/{user_id}**: Delete a user.
- **GET /awx/inventories**: List inventories.
- **GET /awx/inventories/{inventory_id}**: Get an inventory.
- **DELETE /awx/inventories/{inventory_id}**: Delete an inventory.
- **POST /awx/inventories/{inventory_id}/sync**: Sync an inventory.
- **GET /awx/job_templates/{template_id}/schedules**: List schedules for a template.
- **PATCH /awx/schedules/{schedule_id}**: Toggle a schedule.
- **DELETE /awx/schedules/{schedule_id}**: Delete a schedule.
- **GET /awx/templates**: List job templates.
- **GET /awx/jobs**: List jobs with pagination.
- **GET /awx/schedules/{schedule_id}**: Get a schedule.
- **POST /awx/job_templates/{template_id}/schedules**: Create a schedule.
- **GET /awx/projects**: List projects.
- **GET /awx/projects/{project_id}**: Get a project.
- **POST /awx/projects**: Create a project.
- **PATCH /awx/projects/{project_id}**: Update a project.
- **DELETE /awx/projects/{project_id}**: Delete a project.
- **POST /awx/projects/{project_id}/sync**: Sync a project.
- **GET /awx/organizations**: List organizations.
- **GET /awx/organizations/{organization_id}**: Get an organization.
- **POST /awx/organizations**: Create an organization.
- **PATCH /awx/organizations/{organization_id}**: Update an organization.
- **DELETE /awx/organizations/{organization_id}**: Delete an organization.

## Usage Examples
- To launch a job template: Use POST /awx/job_templates/123/launch with optional extra_vars JSON.
- To create a user: POST /awx/users with username, password, and optional fields like first_name, last_name, email.
- To list inventories: GET /awx/inventories.
- To create a schedule: POST /awx/job_templates/123/schedules with name, rrule, and job_template_id.

## Best Practices
- Ensure AWX credentials are configured in settings.
- Handle HTTP errors (e.g., 400 for bad requests, 404 for not found).
- Use pagination for large lists (e.g., jobs).
- Validate inputs to prevent errors.