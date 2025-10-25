#!/usr/bin/env python3
"""
Simple MCP Server Bridge for AWX REST API

This is a lightweight MCP server that bridges LM Studio to the AWX REST API
without requiring external dependencies.
"""

import json
import sys
import urllib.request
import urllib.error
from urllib.parse import urlencode


class AWXMCPServer:
    """Simple MCP server for AWX REST API"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.request_id = 1

    def make_request(
        self, method: str, endpoint: str, data: dict | None = None
    ) -> dict:
        """Make HTTP request to AWX API"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            if method.upper() == "GET":
                if data:
                    url += f"?{urlencode(data)}"
                req = urllib.request.Request(url, headers=headers)
            else:
                data_json = json.dumps(data).encode("utf-8") if data else None
                req = urllib.request.Request(url, data=data_json, headers=headers)

            req.get_method = lambda: method.upper()

            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode("utf-8"))

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else str(e)
            return {"error": f"HTTP {e.code}: {error_body}"}
        except Exception as e:
            return {"error": str(e)}

    def handle_request(self, request: dict) -> dict:
        """Handle MCP protocol requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id", self.request_id)

        response = {"jsonrpc": "2.0", "id": request_id}

        try:
            if method == "initialize":
                response["result"] = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}, "resources": {}},
                    "serverInfo": {"name": "awx-mcp-bridge", "version": "1.0.0"},
                }

            elif method == "tools/list":
                tools = [
                    {
                        "name": "launch_job_template",
                        "description": "Launch an AWX job template",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "template_id": {"type": "integer"},
                                "extra_vars": {"type": "object"},
                            },
                            "required": ["template_id"],
                        },
                    },
                    {
                        "name": "get_job_status",
                        "description": "Get AWX job status",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"job_id": {"type": "integer"}},
                            "required": ["job_id"],
                        },
                    },
                    {
                        "name": "list_templates",
                        "description": "List AWX job templates",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                    {
                        "name": "list_inventories",
                        "description": "List AWX inventories",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                    {
                        "name": "list_jobs",
                        "description": "List AWX jobs",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"page": {"type": "integer", "default": 1}},
                        },
                    },
                ]
                response["result"] = {"tools": tools}

            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})

                if tool_name == "launch_job_template":
                    result = self.make_request(
                        "POST",
                        f"/awx/job_templates/{args['template_id']}/launch",
                        {"extra_vars": args.get("extra_vars", {})},
                    )

                elif tool_name == "get_job_status":
                    result = self.make_request("GET", f"/awx/jobs/{args['job_id']}")

                elif tool_name == "list_templates":
                    result = self.make_request("GET", "/awx/templates")

                elif tool_name == "list_inventories":
                    result = self.make_request("GET", "/awx/inventories")

                elif tool_name == "list_jobs":
                    result = self.make_request(
                        "GET", "/awx/jobs", {"page": args.get("page", 1)}
                    )

                else:
                    result = {"error": f"Unknown tool: {tool_name}"}

                response["result"] = {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                }

            elif method == "resources/list":
                resources = [
                    {
                        "uri": "awx://templates",
                        "name": "Job Templates",
                        "description": "Available AWX job templates",
                        "mimeType": "application/json",
                    },
                    {
                        "uri": "awx://inventories",
                        "name": "Inventories",
                        "description": "AWX inventories",
                        "mimeType": "application/json",
                    },
                    {
                        "uri": "awx://jobs",
                        "name": "Jobs",
                        "description": "AWX jobs",
                        "mimeType": "application/json",
                    },
                ]
                response["result"] = {"resources": resources}

            elif method == "resources/read":
                uri = params.get("uri")

                if uri == "awx://templates":
                    result = self.make_request("GET", "/awx/templates")
                elif uri == "awx://inventories":
                    result = self.make_request("GET", "/awx/inventories")
                elif uri == "awx://jobs":
                    result = self.make_request("GET", "/awx/jobs")
                else:
                    result = {"error": f"Unknown resource: {uri}"}

                response["result"] = {
                    "contents": [{"type": "text", "text": json.dumps(result, indent=2)}]
                }

            else:
                response["error"] = {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                }

        except Exception as e:
            response["error"] = {"code": -32603, "message": str(e)}

        return response


def main():
    """Main MCP server entry point"""
    if len(sys.argv) != 2:
        print("Usage: python3 mcp_server.py <base_url>", file=sys.stderr)
        sys.exit(1)

    base_url = sys.argv[1]

    server = AWXMCPServer(base_url)

    # Send initialization response
    init_response = server.handle_request({"method": "initialize", "id": 1})
    print(json.dumps(init_response))

    # Handle subsequent requests
    try:
        while True:
            line = sys.stdin.readline().strip()
            if not line:
                break

            request = json.loads(line)
            response = server.handle_request(request)
            print(json.dumps(response))

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": str(e)},
                    "id": None,
                }
            )
        )


if __name__ == "__main__":
    main()
