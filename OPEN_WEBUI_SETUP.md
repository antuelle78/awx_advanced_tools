# Open-WebUI Tool Setup Guide

## Prerequisites
- Open-WebUI v0.6.34 or later (check with `docker logs open-webui` or in Admin Panel)
- MCP server running on `http://localhost:8001`
- Both services accessible from the same network

## Step 1: Verify Server Status

Before importing the tool, ensure the MCP server is working:

```bash
# Test server health
curl http://localhost:8001/health
# Should return: {"status":"running"}

# Test AWX connectivity
curl http://localhost:8001/awx/templates
# Should return job templates data
```

## Step 2: Import Tool into Open-WebUI

1. Open Open-WebUI in your browser (usually `http://localhost:3000`)
2. Go to **Admin Panel** → **Tools**
3. Click **Import Tool** or **+ New Tool**
4. Copy entire contents of `open-webui-tool.py` and paste it
5. Click **Save**

## Step 3: Configure Valves

After importing, configure the tool's valves:

1. Click on the **"Ansible AWX Controller"** tool
2. Go to **Valves** section
3. Set the following value:
    - **mcp_server_url**: `http://localhost:8001` (or your server URL)

4. Click **Save**

## Step 4: Enable Tool for Chat

1. Go to your chat interface
2. Click the **Tools** icon (usually in the message input area)
3. Enable **"Ansible AWX Controller"**

## Available Functions

The tool exposes core functions for managing AWX (simplified for better LLM tool usage):

### Job Templates & Jobs
- `list_templates(name)` - List all job templates, optionally filtered by name
- `launch_job_template(template_id, extra_vars)` - Launch a job template
- `list_jobs(page)` - List all jobs with pagination
- `get_job(job_id)` - Get job status and details

### Users & Authentication
- `list_users()` - List all AWX users
- `test_connection()` - Test connection to AWX server

### Inventories & Hosts
- `list_inventories(name)` - List inventories, optionally filtered by name
- `create_inventory(name, organization, variables)` - Create a new inventory
- `get_inventory(inventory_id)` - Get inventory details
- `list_hosts(inventory)` - List hosts, optionally filtered by inventory

### Tool Management
- `get_available_tools()` - Get list of all available tool functions

### Inventories
- `list_inventories()` - List inventories
- `create_inventory(name, organization, variables)` - Create inventory
- `get_inventory(inventory_id)` - Get inventory details
- `delete_inventory(inventory_id)` - Delete inventory
- `sync_inventory(inventory_id)` - Sync inventory

### Schedules
- `list_schedules(template_id)` - List schedules
- `get_schedule(schedule_id)` - Get schedule details
- `create_schedule(name, rrule, job_template_id)` - Create schedule
- `toggle_schedule(schedule_id, enabled)` - Enable/disable schedule
- `delete_schedule(schedule_id)` - Delete schedule

### Organizations
- `list_organizations()` - List organizations
- `get_organization(organization_id)` - Get organization
- `create_organization(name, description)` - Create organization
- `update_organization(organization_id, name, description)` - Update organization
- `delete_organization(organization_id)` - Delete organization

### Projects
- `list_projects()` - List projects
- `get_project(project_id)` - Get project
- `create_project(name, scm_type, scm_url, description)` - Create project
- `update_project(project_id, ...)` - Update project
- `delete_project(project_id)` - Delete project
- `sync_project(project_id)` - Sync project

### Credentials
- `list_credentials()` - List credentials
- `get_credential(credential_id)` - Get credential
- `create_credential(name, credential_type, inputs)` - Create credential
- `update_credential(credential_id, ...)` - Update credential
- `delete_credential(credential_id)` - Delete credential

### Users
- `list_users()` - List users
- `get_user(user_id)` - Get user
- `create_user(username, password, ...)` - Create user
- `update_user(user_id, ...)` - Update user
- `delete_user(user_id)` - Delete user

### Workflow Job Templates
- `list_workflow_job_templates()` - List workflows
- `get_workflow_job_template(workflow_job_template_id)` - Get workflow
- `create_workflow_job_template(name, description)` - Create workflow
- `update_workflow_job_template(workflow_job_template_id, ...)` - Update workflow
- `delete_workflow_job_template(workflow_job_template_id)` - Delete workflow
- `launch_workflow_job_template(workflow_job_template_id, extra_vars)` - Launch workflow

### Notifications
- `list_notifications()` - List notifications
- `get_notification(notification_id)` - Get notification
- `create_notification(name, notification_type, notification_configuration)` - Create notification
- `update_notification(notification_id, ...)` - Update notification
- `delete_notification(notification_id)` - Delete notification

### Instance Groups
- `list_instance_groups()` - List instance groups
- `get_instance_group(instance_group_id)` - Get instance group
- `create_instance_group(name, ...)` - Create instance group
- `update_instance_group(instance_group_id, ...)` - Update instance group
- `delete_instance_group(instance_group_id)` - Delete instance group

### Activity Stream
- `list_activity_stream(page, page_size)` - List activity stream events

## Example Usage

Once configured, you can ask your LLM:

- "List all job templates in AWX"
- "Launch the demo job template"
- "Show me the status of job 123"
- "Create a new inventory called 'production' in organization 1"
- "List all running jobs"
- "What tools are available for AWX operations?"

**Important:** The LLM should use the tool functions directly, not construct API URLs manually. If you see the LLM trying to call endpoints like `/awx/templates`, remind it to use the tool functions instead.

The LLM will automatically use the appropriate tools to interact with your AWX instance.

## Usage Examples

Once configured, you can ask your LLM:

- **"List all job templates in AWX"** → Shows available templates
- **"Launch the demo job template"** → Executes jobs
- **"Show me the status of job 123"** → Checks job progress
- **"Create a new inventory called 'production'"** → Manages resources

## Troubleshooting

### Tool Not Appearing in Open-WebUI

1. **Check Open-WebUI version**: Ensure you're using v0.6.34 or later
2. **Re-import the tool**: Delete and re-import the tool completely
3. **Check tool format**: Ensure the file starts with proper docstring:
   ```python
   """
   title: 'Ansible AWX Controller'
   author: 'Your Name'
   description: 'A tool to interact with Ansible AWX through the MCP Server.'
   requirements:
     - 'httpx'
   """
   ```
4. **Verify class structure**: Ensure `class Tools:` is properly defined

### Connection Errors

1. **Test MCP server**:
   ```bash
   curl http://localhost:8001/health
   # Should return: {"status":"running"}
   ```

2. **Test AWX connectivity**:
   ```bash
   curl http://localhost:8001/awx/templates
   # Should return job templates data
   ```

3. **Check server logs**:
   ```bash
   docker compose logs mcp-server
   ```

4. **Verify network connectivity**: Ensure Open-WebUI can reach `localhost:8001`

### CORS Issues

If you see CORS-related errors in browser console:

1. **Check if CORS is enabled**: The MCP server now includes CORS middleware
2. **Restart services**: `docker compose restart`
3. **Check browser network tab** for preflight OPTIONS requests

### Tool Execution Errors

1. **Check valve configuration**: Ensure `mcp_server_url` is set correctly
2. **Test API endpoints manually**:
   ```bash
   curl "http://localhost:8001/awx/templates"
   ```

3. **Check AWX credentials**: Verify `.env` file has correct AWX settings
4. **Test AWX readiness**:
   ```bash
   curl http://localhost:8001/ready
   ```

### Open-WebUI Specific Issues

1. **Clear browser cache**: Hard refresh (Ctrl+F5) or clear site data
2. **Check Open-WebUI logs**:
   ```bash
   docker logs open-webui
   ```

3. **Restart Open-WebUI**:
   ```bash
   docker restart open-webui
   ```

4. **Check tool permissions**: Ensure the tool is enabled for your user/role

### Recent Open-WebUI Changes (v0.6.34)

- Fixed tool parameter persistence issues
- Improved DELETE request handling for external tools
- Resolved tool ID display problems
- Enhanced filter inlet function execution

If issues persist after these checks, try:
1. Update both Open-WebUI and MCP server to latest versions
2. Check GitHub issues for similar problems
3. Join the Open-WebUI Discord for community support
