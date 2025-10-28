# Simplified Open-WebUI Configuration for AWX Integration

## Prerequisites
- Open-WebUI installed and running
- MCP server deployed on `http://localhost:8001` (as per previous deployment)

## Step 1: Import the Tool
1. Open Open-WebUI in your browser
2. Go to **Admin Panel** → **Tools**
3. Click **Import Tool** or **+ New Tool**
4. Copy the entire content of `open-webui-tool.py` and paste it into the tool editor
5. Click **Save**

## Step 2: Configure the Tool
1. In the Tools list, click on the **"Ansible AWX Controller"** tool
2. Go to the **Valves** section
3. Set the following:
   - **mcp_server_url**: `http://localhost:8001`
4. Click **Save**

## Step 3: Enable in Chat
1. Go to your chat interface
2. Click the **Tools** icon (usually in the message input area)
3. Enable **"Ansible AWX Controller"**

## Usage Examples
Once configured, you can ask your LLM:
- "List all job templates in AWX"
- "Launch job template 5"
- "Show me the status of job 123"
- "Create a new inventory called 'production'"

## Troubleshooting
- Ensure the MCP server is running: `docker compose ps`
- Check Open-WebUI logs for any errors
- Verify the `mcp_server_url` is accessible from Open-WebUI

## Available Functions
The tool provides 58 functions for AWX management, including job templates, inventories, organizations, projects, credentials, users, workflows, notifications, instance groups, and activity streams.