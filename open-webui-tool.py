"""
title: Ansible AWX Controller
author: Michael Nelson
description: A tool to interact with Ansible AWX through the MCP Server.
requirements: httpx
"""

import httpx
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json
import time


class PromptOptimizer:
    """Optimizes prompts for better LLM tool usage success rate."""

    def __init__(self):
        self.tool_prompts = self._load_tool_prompts()
        self.confidence_threshold = 0.8
        self.log_file = "tool_usage.log"

    def _load_tool_prompts(self) -> Dict[str, str]:
        """Load optimized prompts for each tool."""
        return {
            "list_templates": "Think step by step: 1. Understand the request for job templates. 2. Call list_templates with name parameter to filter. 3. Use the results to inform further actions. Example: list_templates(name='Demo Job Template') to find specific template.",
            "launch_job_template": "Think step by step: 1. Identify the template_id from list_templates. 2. Prepare extra_vars if needed. 3. Call launch_job_template. Example: template_id=123, extra_vars={'branch': 'main'}.",
            "list_jobs": "Think step by step: 1. Check if pagination is needed. 2. Call list_jobs with page if specified. 3. Review job statuses. Example: page=1 to get the first page of jobs.",
            "get_job": "Think step by step: 1. Get the job_id from list_jobs. 2. Call get_job to check status. 3. Act based on the result. Example: job_id=456 to check if the job is running.",
            "list_inventories": "Think step by step: 1. List inventories to find IDs by name. 2. Use name parameter to filter. 3. Use for other operations. Example: list_inventories(name='Sample Inventory 1') to find specific inventory.",
            "create_inventory": "Think step by step: 1. Use list_organizations to get valid org ID. 2. Check if name exists. 3. Call create_inventory with name, org, variables. Example: name='infra', organization=2, variables={'ansible_user': 'admin'}.",
            "get_inventory": "Think step by step: 1. Get inventory_id from list_inventories. 2. Call get_inventory. 3. Use details for further actions. Example: inventory_id=789.",
            "delete_inventory": "Think step by step: 1. Confirm deletion with confirm=true. 2. Use dry_run if testing. 3. Call delete_inventory. Example: inventory_id=789, confirm=true.",
            "sync_inventory": "Think step by step: 1. Get inventory_id. 2. Call sync_inventory. 3. Monitor the job. Example: inventory_id=789.",
            "list_users": "Think step by step: 1. List users to find IDs. 2. Use for other operations. 3. Ensure no duplicates. Example: Call this before creating.",
            "list_hosts": "Think step by step: 1. List hosts to see what's available. 2. Use inventory parameter to filter by inventory. 3. Use for other operations. Example: list_hosts(inventory=5) to see hosts in a specific inventory.",
            "get_user": "Think step by step: 1. Get user_id from list_users. 2. Call get_user. 3. Use details. Example: user_id=2.",
            "create_user": "Think step by step: 1. Check if username exists. 2. Call create_user. 3. Verify creation. Example: username='newuser', password='pass123'.",
            "update_user": "Think step by step: 1. Get user_id. 2. Call update_user. 3. Confirm changes. Example: user_id=2, first_name='John'.",
            "delete_user": "Think step by step: 1. Confirm deletion. 2. Call delete_user. 3. Verify removal. Example: user_id=2.",
        }

    def get_optimized_prompt(self, tool_name: str, **kwargs) -> str:
        """Get an optimized prompt for a specific tool."""
        if tool_name in self.tool_prompts:
            return self.tool_prompts[tool_name]
        return f"Use the {tool_name} tool appropriately."

    def log_tool_usage(self, tool_name: str, success: bool, response_time: float):
        """Log tool usage for feedback loop."""
        try:
            with open(self.log_file, "a") as f:
                f.write(f"{time.time()},{tool_name},{success},{response_time}\n")
        except Exception:
            pass  # Ignore logging errors


class Tools:
    class Valves(BaseModel):
        mcp_server_url: str = Field(
            default="http://localhost:31005",
            description="The base URL of MCP server. For k3s deployment, use the gateway NodePort (default: http://<k3s-node-ip>:31005). For local Docker, use http://host.docker.internal:8001.",
        )
        mcp_username: str = Field(
            default="awxai", description="Username for MCP server authentication."
        )
        mcp_password: str = Field(
            default="fuckoffnoW", description="Password for MCP server authentication."
        )

    def __init__(self):
        self.valves = self.Valves()
        self.client = httpx.Client(
            timeout=30.0, auth=(self.valves.mcp_username, self.valves.mcp_password)
        )
        self.prompt_optimizer = PromptOptimizer()

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {"Content-Type": "application/json"}

    @property
    def mcp_server_url(self) -> str:
        return self.valves.mcp_server_url

    def get_optimized_prompt(self, tool_name: str, **kwargs) -> str:
        """Get an optimized prompt for a specific tool."""
        return self.prompt_optimizer.get_optimized_prompt(tool_name, **kwargs)

    def log_tool_usage(self, tool_name: str, success: bool, response_time: float):
        """Log tool usage for feedback loop."""
        self.prompt_optimizer.log_tool_usage(tool_name, success, response_time)

    def list_templates(self, name: Optional[str] = None) -> str:
        """
        Lists all job templates in AWX, optionally filtered by name.

        IMPORTANT: This is a tool function - do not construct API URLs manually.
        Use this function directly instead of calling endpoints like /awx/templates.

        :param name: Optional name to filter job templates (e.g., 'Demo Job Template')
        :return: A JSON string containing a list of job templates.

        Example usage:
        - list_templates() - lists all templates
        - list_templates(name='Demo Job Template') - filters by name
        """
        url = f"{self.mcp_server_url}/awx/templates"
        params = {}
        if name:
            params["name"] = name
        try:
            response = self.client.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})

    def launch_job_template(
        self, template_id: int, extra_vars: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Launches an AWX job template to start a new job.

        IMPORTANT: This is a tool function - do not construct API URLs manually.
        Use this function directly instead of calling endpoints like /awx/job_templates/{id}/launch.

        :param template_id: The ID of job template to launch (get from list_templates first)
        :param extra_vars: A dictionary of extra variables to pass to job (optional)
        :return: A JSON string containing details of newly created job.

        Example usage:
        - launch_job_template(template_id=123) - launch with default vars
        - launch_job_template(template_id=123, extra_vars={'branch': 'main'}) - with extra vars
        """
        url = f"{self.mcp_server_url}/awx/job_templates/{template_id}/launch"
        payload: Dict[str, Any] = {}
        if extra_vars:
            payload["extra_vars"] = extra_vars

        try:
            response = self.client.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_job(self, job_id: int) -> str:
        """
        Retrieves current status and details of a specific job.

        IMPORTANT: This is a tool function - do not construct API URLs manually.
        Use this function directly instead of calling endpoints like /awx/jobs/{id}.

        :param job_id: The ID of job to retrieve (get from list_jobs or launch_job_template)
        :return: A JSON string containing status and details of job.

        Example usage:
        - get_job(job_id=456) - check status of job 456
        """
        url = f"{self.mcp_server_url}/awx/jobs/{job_id}"
        try:
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})

    def list_jobs(self, page: int = 1) -> str:
        """
        Lists all jobs in AWX with pagination.

        IMPORTANT: This is a tool function - do not construct API URLs manually.
        Use this function directly instead of calling endpoints like /awx/jobs.

        :param page: The page number for pagination (default: 1)
        :return: A JSON string containing a list of jobs.

        Example usage:
        - list_jobs() - list first page of jobs
        - list_jobs(page=2) - list second page
        """
        url = f"{self.mcp_server_url}/awx/jobs?page={page}"
        try:
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})

    def list_inventories(self, name: Optional[str] = None) -> str:
        """
        Lists all inventories in AWX, optionally filtered by name.

        IMPORTANT: This is a tool function - do not construct API URLs manually.
        Use this function directly instead of calling endpoints like /awx/inventories.

        :param name: Optional name to filter inventories
        :return: A JSON string containing a list of inventories.

        Example usage:
        - list_inventories() - list all inventories
        - list_inventories(name='Sample Inventory 1') - filter by name
        """
        url = f"{self.mcp_server_url}/awx/inventories"
        params = {}
        if name:
            params["name"] = name
        try:
            response = self.client.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})

    def create_inventory(self, name: str, organization: int, variables: Optional[Dict[str, Any]] = None) -> str:
        """
        Creates a new inventory in AWX.

        IMPORTANT: This is a tool function - do not construct API URLs manually.
        Use this function directly instead of calling endpoints like /awx/inventories.

        :param name: Name of the new inventory
        :param organization: Organization ID for the inventory
        :param variables: Optional variables dictionary
        :return: A JSON string containing the created inventory details.

        Example usage:
        - create_inventory(name='infra', organization=2, variables={'ansible_user': 'admin'})
        """
        url = f"{self.mcp_server_url}/awx/inventories"
        payload = {
            "name": name,
            "organization": organization
        }
        if variables:
            payload["variables"] = variables

        try:
            response = self.client.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_inventory(self, inventory_id: int) -> str:
        """
        Retrieves details of a specific inventory.

        IMPORTANT: This is a tool function - do not construct API URLs manually.
        Use this function directly instead of calling endpoints like /awx/inventories/{id}.

        :param inventory_id: The ID of the inventory to retrieve
        :return: A JSON string containing inventory details.

        Example usage:
        - get_inventory(inventory_id=789)
        """
        url = f"{self.mcp_server_url}/awx/inventories/{inventory_id}"
        try:
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})

    def list_hosts(self, inventory: Optional[int] = None) -> str:
        """
        Lists all hosts in AWX, optionally filtered by inventory.

        IMPORTANT: This is a tool function - do not construct API URLs manually.
        Use this function directly instead of calling endpoints like /awx/hosts.

        :param inventory: Optional inventory ID to filter hosts
        :return: A JSON string containing a list of hosts.

        Example usage:
        - list_hosts() - list all hosts
        - list_hosts(inventory=5) - list hosts in inventory 5
        """
        url = f"{self.mcp_server_url}/awx/hosts"
        params = {}
        if inventory:
            params["inventory"] = inventory
        try:
            response = self.client.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})
        url = f"{self.mcp_server_url}/awx/users"
        try:
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})

    def test_connection(self) -> str:
        """
        Tests the connection to the AWX server.

        IMPORTANT: This is a tool function - do not construct API URLs manually.
        Use this function directly instead of calling endpoints like /awx/test.

        :return: A JSON string containing test results.

        Example usage:
        - test_connection() - verify AWX connectivity
        """
        url = f"{self.mcp_server_url}/awx/test"
        try:
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_available_tools(self) -> str:
        """
        Returns a list of all available tool functions for AWX operations.

        Use this to see what functions are available instead of guessing API endpoints.
        Always use the tool functions listed here rather than constructing API URLs manually.

        :return: A JSON string containing available tool functions and their descriptions.
        """
        tools_info = {
            "list_templates": "List job templates, optionally filtered by name",
            "launch_job_template": "Launch a job template with optional extra variables",
            "get_job": "Get status and details of a specific job",
            "list_jobs": "List all jobs with pagination",
            "list_users": "List all AWX users",
            "list_inventories": "List inventories, optionally filtered by name",
            "create_inventory": "Create a new inventory",
            "get_inventory": "Get details of a specific inventory",
            "list_hosts": "List hosts, optionally filtered by inventory",
            "test_connection": "Test connection to AWX server",
            "get_available_tools": "Get this list of available tools"
        }
        return json.dumps({
            "message": "Use these tool functions instead of constructing API URLs manually",
            "available_tools": tools_info,
            "important": "Do not call endpoints like /awx/templates, /awx/jobs, etc. Use the functions above."
        })
        url = f"{self.mcp_server_url}/awx/test"
        try:
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})