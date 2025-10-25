# LM Studio Integration Guide

## Overview

This guide explains how to integrate your AWX MCP server with LM Studio using the Model Context Protocol (MCP). LM Studio supports MCP servers starting from version 0.3.17.

## Method 1: Direct REST API Integration (Recommended)

Since LM Studio doesn't natively support REST APIs as MCP servers, the most straightforward approach is to use the Open-WebUI tool integration or create a simple MCP bridge.

### Option A: Use Open-WebUI Tool (Already Configured)

1. **Import the Open-WebUI Tool**:
   ```bash
   # Copy the tool content
   cat open-webui-tool.py
   ```

2. **Import into Open-WebUI**:
   - Go to Open-WebUI Admin Panel → Tools
   - Click "Import Tool" or "+ New Tool"
   - Paste the entire content of `open-webui-tool.py`
   - Click Save

3. **Configure Valves**:
   - `mcp_server_url`: `http://localhost:8001`


4. **Enable in Chat**:
   - Go to chat interface
   - Click tools icon
   - Enable "Ansible AWX Controller"

### Option B: Create MCP Bridge Script

If you want a more direct MCP integration, you can create a simple bridge script:

```python
#!/usr/bin/env python3
"""
Simple MCP Bridge for AWX REST API
Run this script to create an MCP server that LM Studio can connect to
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List

import httpx


class AWXBridge:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            headers={

                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            if method == "tools/list":
                tools = [
                    {
                        "name": "launch_job_template",
                        "description": "Launch an AWX job template",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "template_id": {"type": "integer"},
                                "extra_vars": {"type": "object"}
                            },
                            "required": ["template_id"]
                        }
                    },
                    {
                        "name": "get_job_status",
                        "description": "Get AWX job status",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "job_id": {"type": "integer"}
                            },
                            "required": ["job_id"]
                        }
                    },
                    {
                        "name": "list_inventories",
                        "description": "List AWX inventories",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "list_templates",
                        "description": "List AWX job templates",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "list_jobs",
                        "description": "List AWX jobs",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "page": {"type": "integer", "default": 1}
                            }
                        }
                    }
                ]
                return {"tools": tools}

            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})

                if tool_name == "launch_job_template":
                    response = await self.client.post(
                        f"{self.base_url}/awx/job_templates/{args['template_id']}/launch",
                        json={"extra_vars": args.get("extra_vars", {})}
                    )
                    result = response.json()

                elif tool_name == "get_job_status":
                    response = await self.client.get(f"{self.base_url}/awx/jobs/{args['job_id']}")
                    result = response.json()

                elif tool_name == "list_inventories":
                    response = await self.client.get(f"{self.base_url}/awx/inventories")
                    result = response.json()

                elif tool_name == "list_templates":
                    response = await self.client.get(f"{self.base_url}/awx/templates")
                    result = response.json()

                elif tool_name == "list_jobs":
                    page = args.get("page", 1)
                    response = await self.client.get(f"{self.base_url}/awx/jobs?page={page}")
                    result = response.json()

                else:
                    result = {"error": f"Unknown tool: {tool_name}"}

                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

            elif method == "resources/list":
                resources = [
                    {
                        "uri": "awx://templates",
                        "name": "Job Templates",
                        "description": "Available AWX job templates",
                        "mimeType": "application/json"
                    },
                    {
                        "uri": "awx://inventories",
                        "name": "Inventories",
                        "description": "AWX inventories",
                        "mimeType": "application/json"
                    },
                    {
                        "uri": "awx://jobs",
                        "name": "Jobs",
                        "description": "AWX jobs",
                        "mimeType": "application/json"
                    }
                ]
                return {"resources": resources}

            elif method == "resources/read":
                uri = params.get("uri")

                if uri == "awx://templates":
                    response = await self.client.get(f"{self.base_url}/awx/templates")
                    data = response.json()
                elif uri == "awx://inventories":
                    response = await self.client.get(f"{self.base_url}/awx/inventories")
                    data = response.json()
                elif uri == "awx://jobs":
                    response = await self.client.get(f"{self.base_url}/awx/jobs")
                    data = response.json()
                else:
                    data = {"error": f"Unknown resource: {uri}"}

                return {"contents": [{"type": "text", "text": json.dumps(data, indent=2)}]}

            else:
                return {"error": {"code": -32601, "message": f"Method not found: {method}"}}

        except Exception as e:
            return {"error": {"code": -32603, "message": str(e)}}


async def main():
    """Main MCP bridge server"""
    if len(sys.argv) != 3:
        print("Usage: python3 mcp_bridge.py <base_url>")
        sys.exit(1)

    base_url = sys.argv[1]

    bridge = AWXBridge(base_url)

    # Initialize MCP handshake
    print(json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {}
            },
            "serverInfo": {
                "name": "awx-mcp-bridge",
                "version": "1.0.0"
            }
        }
    }))

    # Handle requests
    try:
        while True:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break

            request = json.loads(line.strip())
            response = await bridge.handle_request(request)

            print(json.dumps({
                "jsonrpc": "2.0",
                "id": request.get("id"),
                **response
            }))

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    asyncio.run(main())
```

## Method 2: LM Studio MCP Configuration

### Step 1: Create MCP Configuration

1. **Copy the mcp.json configuration**:
   ```bash
   cp mcp.json ~/.lmstudio/mcp.json
   ```

2. **Edit the configuration** to match your setup:
   ```json
   {
     "mcpServers": {
       "awx-rest-bridge": {
         "url": "http://localhost:8001",
         "headers": {

           "Content-Type": "application/json",
           "Accept": "application/json"
         },
         "description": "AWX REST API Bridge for LM Studio",
         "capabilities": ["tools", "resources"],
         "tools": [
           // ... tool definitions from mcp.json
         ],
         "resources": [
           // ... resource definitions from mcp.json
         ]
       }
     }
   }
   ```

### Step 2: Restart LM Studio

1. Close LM Studio completely
2. Restart LM Studio
3. The MCP server should appear in the tools section

## Method 3: Using Existing MCP Tools

Since creating a full MCP server is complex, you can use existing MCP tools that work with REST APIs:

### Option A: Use MCP-REST-API Bridge

1. **Install an existing MCP-REST bridge**:
   ```bash
   # Example: Install a generic REST API MCP server
   npm install -g mcp-rest-api
   ```

2. **Configure it to point to your AWX server**:
   ```json
   {
     "mcpServers": {
       "awx-api": {
         "command": "mcp-rest-api",
         "args": ["--url", "http://localhost:8001", "--auth", "Bearer eyJ..."],
         "cwd": "/path/to/awx/server"
       }
     }
   }
   ```

### Option B: Use Cursor's MCP Integration

If you're using Cursor IDE, it has better MCP support:

1. **Create Cursor MCP configuration**:
   ```json
   {
     "mcpServers": {
       "awx": {
         "url": "http://localhost:8001/awx/",
         "headers": {

         }
       }
     }
   }
   ```

2. **Save as `~/.cursor/mcp.json`**

## Testing the Integration

### Test with curl:
```bash
# Test authentication
curl
     http://localhost:8001/awx/templates

# Test job launch
curl -X POST \

  -H "Content-Type: application/json" \
  -d '{"extra_vars": {"host": "webserver"}}' \
  http://localhost:8001/awx/job_templates/1/launch
```

### Test in LM Studio:
1. Open LM Studio
2. Start a chat with any model
3. Ask: "List all job templates in AWX"
4. The model should use the MCP tools to fetch the data

## Troubleshooting

### Common Issues:

1. **MCP Server Not Detected**:
   - Ensure LM Studio is version 0.3.17 or later
   - Check `mcp.json` syntax
   - Restart LM Studio after configuration changes

2. **Authentication Errors**:
   - Verify JWT token is valid
   - Check token expiration
   - Regenerate token if needed

3. **Connection Errors**:
   - Ensure AWX server is running: `docker compose ps`
   - Check server URL in configuration
   - Verify firewall settings

4. **Tool Not Working**:
   - Check server logs: `docker compose logs mcp-server`
   - Verify API endpoints are accessible
   - Test with curl first

### Debug Commands:

```bash
# Check server status
docker compose ps

# View server logs
docker compose logs mcp-server

# Test API endpoints
curl http://localhost:8001/awx/templates

# Test connection
curl http://localhost:8001/awx/templates

# Check LM Studio MCP configuration
cat ~/.lmstudio/mcp.json
```

## Available Tools

Once integrated, your LLM will have access to these AWX management functions:

- **Job Management**: Launch templates, check job status, list jobs
- **Inventory Management**: List, create, sync inventories
- **Organization Management**: List, create, update organizations
- **Project Management**: List, create, sync projects
- **Schedule Management**: List, create, toggle schedules
- **Resource Discovery**: Browse templates, inventories, jobs

## Example Conversations

With the integration working, you can ask your LLM:

- "Show me all available job templates"
- "Launch the web server deployment template"
- "What's the status of job 123?"
- "Create a new inventory called 'production'"
- "List all organizations in AWX"
- "Sync the main project"

The LLM will automatically use the appropriate tools to interact with your AWX instance!