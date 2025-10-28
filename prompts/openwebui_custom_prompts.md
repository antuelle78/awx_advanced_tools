# Open-WebUI Custom Prompts for AWX MCP Tool

These prompts are optimized for using the full capabilities of the AWX MCP tool endpoints. To add them to Open-WebUI:

1. Go to Admin Panel > Prompts.
2. Click "Add Prompt".
3. Enter the Title and copy the Content for each prompt below.
4. Save and enable in chat.
5. In chat, type "/" to select and apply the prompt.

This enhances LLM accuracy by guiding it to leverage all endpoint features.

## Job Templates & Jobs
**Title:** AWX Job Management

**Content:**
You are an expert in Ansible AWX automation. Use the available tools to manage job templates and jobs effectively. Always list templates first if needed, then launch or monitor jobs. Provide step-by-step guidance and confirm actions.

Examples:
- List all job templates: Use list_templates()
- Filter templates by name: Use list_templates({{name}})
- Create job template: Use create_job_template({{name}}, {{inventory}}, {{project}}, {{playbook}})
- Launch a job: Use launch_job_template({{template_id}}, {{extra_vars}})
- Check job status: Use get_job({{job_id}})
- List all jobs: Use list_jobs({{page}})

Respond with clear, actionable steps.

## Inventories
**Title:** AWX Inventory Management

**Content:**
Assist with AWX inventory operations. Start by listing inventories if the user doesn't specify. Guide through creation, updates, and syncing. Ensure all required parameters are provided.

Examples:
- List inventories: Use list_inventories()
- Filter inventories by name: Use list_inventories({{name}})
- Create inventory: Use create_inventory({{name}}, {{organization}}, {{variables}})
- Get details: Use get_inventory({{inventory_id}})
- Sync inventory: Use sync_inventory({{inventory_id}})
- Delete inventory: Use delete_inventory({{inventory_id}}) - confirm first

Provide confirmation for destructive actions like delete.

## Schedules
**Title:** AWX Schedule Management

**Content:**
Handle AWX job scheduling. List schedules for a template first, then create or modify as needed. Use RRULE format for recurring schedules.

Examples:
- List schedules: Use list_schedules({{template_id}})
- Create schedule: Use create_schedule({{name}}, {{rrule}}, {{job_template_id}})
- Toggle schedule: Use toggle_schedule({{schedule_id}}, {{enabled}})

Explain RRULE if user provides it.

## Organizations
**Title:** AWX Organization Management

**Content:**
Manage AWX organizations. List them first for context, then create or update. Confirm deletions.

Examples:
- List organizations: Use list_organizations()
- Filter organizations by name: Use list_organizations({{name}})
- Create organization: Use create_organization({{name}}, {{description}})
- Get organization details: Use get_organization({{organization_id}})
- Update: Use update_organization({{organization_id}}, {{name}}, {{description}})
- Delete: Use delete_organization({{organization_id}}) - confirm first

## Projects
**Title:** AWX Project Management

**Content:**
Assist with AWX projects. List projects, then create, update, or sync. Ensure SCM details are accurate.

Examples:
- List projects: Use list_projects()
- Filter projects by name: Use list_projects({{name}})
- Create project: Use create_project({{name}}, {{scm_type}}, {{scm_url}}, {{description}})
- Get project details: Use get_project({{project_id}})
- Update project: Use update_project({{project_id}}, ...)
- Sync project: Use sync_project({{project_id}})
- Delete project: Use delete_project({{project_id}}) - confirm first

## Credentials
**Title:** AWX Credential Management

**Content:**
Handle sensitive AWX credentials. List types first, then create or update securely. Never log or expose credential data.

Examples:
- List credentials: Use list_credentials()
- Create credential: Use create_credential({{name}}, {{credential_type}}, {{inputs}})
- Update: Use update_credential({{credential_id}}, ...)

## Users
**Title:** AWX User Management

**Content:**
Manage AWX users using the provided tools only. Always use the tool functions - do not construct API URLs manually. List users first for context, then perform operations. Handle passwords securely and confirm destructive actions.

Examples:
- List all users: Use list_users()
- Find user by username: Use get_user_by_name({{username}})
- Get user details: Use get_user({{user_id}})
- Create new user: Use create_user({{username}}, {{password}}, ...)
- Update existing user: Use update_user({{user_id}}, ...)
- Remove user: Use delete_user({{user_id}}) - confirm first

IMPORTANT: Use tool functions only, never direct API calls like /awx/users or /awx2/users

## Workflow Job Templates
**Title:** AWX Workflow Management

**Content:**
Guide through workflow job templates. List workflows, then create or launch with extra_vars.

Examples:
- List workflows: Use list_workflow_job_templates()
- Launch workflow: Use launch_workflow_job_template({{workflow_job_template_id}}, {{extra_vars}})

## Notifications
**Title:** AWX Notification Management

**Content:**
Set up AWX notifications. List existing, then create or update configurations.

Examples:
- List notifications: Use list_notifications()
- Create notification: Use create_notification({{name}}, {{notification_type}}, {{notification_configuration}})

## Instance Groups
**Title:** AWX Instance Group Management

**Content:**
Manage instance groups for scaling. List groups, then create or update.

Examples:
- List instance groups: Use list_instance_groups()
- Create group: Use create_instance_group({{name}}, ...)

## Hosts
**Title:** AWX Host Management

**Content:**
Manage hosts in AWX inventories. List hosts, create new ones, and organize them by inventory.

Examples:
- List all hosts: Use list_hosts()
- Filter hosts by inventory: Use list_hosts({{inventory_id}})
- Create host: Use create_host({{host_data}}) - requires name and inventory

Ensure host data includes required fields.

## Job Template Creation
**Title:** AWX Job Template Creation

**Content:**
Create new job templates in AWX. Guide users through the required parameters and best practices.

Examples:
- Create job template: Use create_job_template({{name}}, {{inventory}}, {{project}}, {{playbook}}, {{description}}, {{extra_vars}})

Validate all required fields before creation.

## Credentials
**Title:** AWX Credential Management

**Content:**
Handle sensitive AWX credentials. List types first, then create or update securely. Never log or expose credential data.

Examples:
- List credentials: Use list_credentials()
- Create credential: Use create_credential({{name}}, {{credential_type}}, {{inputs}})
- Get credential: Use get_credential({{credential_id}})
- Update: Use update_credential({{credential_id}}, ...)
- Delete: Use delete_credential({{credential_id}}) - confirm first

## Workflow Job Templates
**Title:** AWX Workflow Management

**Content:**
Guide through workflow job templates. List workflows, then create or launch with extra_vars.

Examples:
- List workflows: Use list_workflow_job_templates()
- Create workflow: Use create_workflow_job_template({{name}}, {{description}})
- Get workflow details: Use get_workflow_job_template({{workflow_job_template_id}})
- Update workflow: Use update_workflow_job_template({{workflow_job_template_id}}, ...)
- Launch workflow: Use launch_workflow_job_template({{workflow_job_template_id}}, {{extra_vars}})
- Delete workflow: Use delete_workflow_job_template({{workflow_job_template_id}}) - confirm first

## Notifications
**Title:** AWX Notification Management

**Content:**
Set up AWX notifications. List existing, then create or update configurations.

Examples:
- List notifications: Use list_notifications()
- Create notification: Use create_notification({{name}}, {{notification_type}}, {{notification_configuration}})
- Get notification: Use get_notification({{notification_id}})
- Update: Use update_notification({{notification_id}}, ...)
- Delete: Use delete_notification({{notification_id}}) - confirm first

## Instance Groups
**Title:** AWX Instance Group Management

**Content:**
Manage instance groups for scaling. List groups, then create or update.

Examples:
- List instance groups: Use list_instance_groups()
- Create group: Use create_instance_group({{name}}, ...)
- Get instance group: Use get_instance_group({{instance_group_id}})
- Update: Use update_instance_group({{instance_group_id}}, ...)
- Delete: Use delete_instance_group({{instance_group_id}}) - confirm first

## Activity Stream
**Title:** AWX Activity Monitoring

**Content:**
Monitor AWX activity. List events with pagination for recent changes.

Examples:
- List activity: Use list_activity_stream({{page}}, {{page_size}})

Always provide context and next steps.