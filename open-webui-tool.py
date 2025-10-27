"""
title: Ansible AWX Controller
author: Michael Nelson
description: A tool to interact with Ansible AWX through the MCP Server.
requirements:
  - httpx
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
            default="http://host.docker.internal:8001",
            description="The base URL of MCP server.",
        )
        mcp_username: str = Field(
            default="openwebui", description="Username for MCP server authentication."
        )
        mcp_password: str = Field(
            default="openwebui", description="Password for MCP server authentication."
        )

    def __init__(self):
        self.valves = self.Valves()
        self.client = httpx.Client(
            timeout=30.0, auth=(self.valves.mcp_username, self.valves.mcp_password)
        )  # Add timeout and auth for requests
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

    def get_all_optimized_prompts(self) -> Dict[str, str]:
        """Get optimized prompts for all available tools."""
        return self.prompt_optimizer.tool_prompts

    def list_templates(self, name: Optional[str] = None) -> str:
        """
        Lists all job templates in AWX, optionally filtered by name.

        :param name: Optional name to filter job templates
        :return: A JSON string containing a list of job templates.

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

        :param template_id: The ID of job template to launch.
        :param extra_vars: A dictionary of extra variables to pass to job.
        :return: A JSON string containing details of newly created job.
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

        :param job_id: The ID of job to retrieve.
        :return: A JSON string containing status and details of job.
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

        :param page: The page number for pagination.
        :return: A JSON string containing a list of jobs.
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

    def create_job_template(
        self,
        name: str,
        inventory: int,
        project: int,
        playbook: str,
        description: Optional[str] = None,
        extra_vars: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Creates a new job template in AWX.

        :param name: Name of the job template.
        :param inventory: ID of the inventory to use.
        :param project: ID of the project containing the playbook.
        :param playbook: Path to the playbook file.
        :param description: Optional description.
        :param extra_vars: Optional extra variables.
        :return: A JSON string containing the created job template details.
        """
        url = f"{self.mcp_server_url}/awx/job_templates/"
        payload = {
            "name": name,
            "inventory": inventory,
            "project": project,
            "playbook": playbook,
        }
        if description:
            payload["description"] = description
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

    # Inventory Management
    def list_inventories(self, name: Optional[str] = None) -> str:
        """
        Lists all inventories in AWX, optionally filtered by name.

        :param name: Optional name to filter inventories
        :return: A JSON string containing a list of inventories.
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

    def create_inventory(
        self, name: str, organization: int, variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Creates a new inventory in AWX.

        :param name: Name of the inventory.
        :param organization: ID of the organization.
        :param variables: Optional variables for the inventory.
        :return: A JSON string containing the created inventory details.
        """
        url = f"{self.mcp_server_url}/awx/inventories"
        payload = {"name": name, "organization": organization}
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

        :param inventory_id: The ID of inventory to retrieve.
        :return: A JSON string containing inventory details.
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

    def sync_inventory(self, inventory_id: int) -> str:
        """
        Synchronizes an inventory with its source.

        :param inventory_id: The ID of inventory to sync.
        :return: A JSON string containing sync job details.
        """
        url = f"{self.mcp_server_url}/awx/inventories/{inventory_id}/sync"
        try:
            response = self.client.post(url, headers=self._get_headers())
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

    # Project Management
    def list_projects(self, name: Optional[str] = None) -> str:
        """
        Lists all projects in AWX, optionally filtered by name.

        :param name: Optional name to filter projects
        :return: A JSON string containing a list of projects.
        """
        url = f"{self.mcp_server_url}/awx/projects"
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

    def create_project(
        self, name: str, scm_type: str, scm_url: str, description: Optional[str] = None
    ) -> str:
        """
        Creates a new project in AWX.

        :param name: Name of the project.
        :param scm_type: Type of source control (git, svn, etc.).
        :param scm_url: URL of the source repository.
        :param description: Optional description.
        :return: A JSON string containing the created project details.
        """
        url = f"{self.mcp_server_url}/awx/projects"
        payload = {"name": name, "scm_type": scm_type, "scm_url": scm_url}
        if description:
            payload["description"] = description

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

    def sync_project(self, project_id: int) -> str:
        """
        Synchronizes a project with its source repository.

        :param project_id: The ID of project to sync.
        :return: A JSON string containing sync job details.
        """
        url = f"{self.mcp_server_url}/awx/projects/{project_id}/sync"
        try:
            response = self.client.post(url, headers=self._get_headers())
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

    # Organization Management
    def list_organizations(self, name: Optional[str] = None) -> str:
        """
        Lists all organizations in AWX, optionally filtered by name.

        :param name: Optional name to filter organizations
        :return: A JSON string containing a list of organizations.
        """
        url = f"{self.mcp_server_url}/awx/organizations"
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

    def create_organization(self, name: str, description: Optional[str] = None) -> str:
        """
        Creates a new organization in AWX.

        :param name: Name of the organization.
        :param description: Optional description.
        :return: A JSON string containing the created organization details.
        """
        url = f"{self.mcp_server_url}/awx/organizations"
        payload = {"name": name}
        if description:
            payload["description"] = description

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

    # Host Management
    def list_hosts(self, inventory: Optional[int] = None) -> str:
        """
        Lists all hosts in AWX, optionally filtered by inventory.

        :param inventory: Optional inventory ID to filter hosts
        :return: A JSON string containing a list of hosts.
        """
        url = f"{self.mcp_server_url}/awx/hosts/"
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

    def create_host(self, host_data: Dict[str, Any]) -> str:
        """
        Creates a new host in AWX.

        :param host_data: A dictionary containing host details (name, inventory, etc.).
        :return: A JSON string containing the created host details.
        """
        url = f"{self.mcp_server_url}/awx/hosts/"
        try:
            response = self.client.post(
                url, headers=self._get_headers(), json=host_data
            )
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

    # User Management
    def list_users(self) -> str:
        """
        Lists all users in AWX.

        :return: A JSON string containing a list of users.
        """
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

    def create_user(
        self,
        username: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> str:
        """
        Creates a new user in AWX.

        :param username: Username for the new user.
        :param password: Password for the new user.
        :param first_name: Optional first name.
        :param last_name: Optional last name.
        :param email: Optional email address.
        :return: A JSON string containing the created user details.
        """
        url = f"{self.mcp_server_url}/awx/users"
        payload = {"username": username, "password": password}
        if first_name:
            payload["first_name"] = first_name
        if last_name:
            payload["last_name"] = last_name
        if email:
            payload["email"] = email

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

    def get_user(self, user_id: int) -> str:
        """
        Retrieves details of a specific user.

        :param user_id: The ID of user to retrieve.
        :return: A JSON string containing user details.
        """
        url = f"{self.mcp_server_url}/awx/users/{user_id}"
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

    def get_user_by_name(self, username: str) -> str:
        """
        Retrieves user details by username.

        :param username: The username to search for.
        :return: A JSON string containing user details.
        """
        url = f"{self.mcp_server_url}/awx/users/by-name/{username}"
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

    def update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> str:
        """
        Updates an existing user in AWX.

        :param user_id: The ID of user to update.
        :param username: Optional new username.
        :param first_name: Optional new first name.
        :param last_name: Optional new last name.
        :param email: Optional new email address.
        :return: A JSON string containing the updated user details.
        """
        url = f"{self.mcp_server_url}/awx/users/{user_id}"
        payload = {}
        if username:
            payload["username"] = username
        if first_name:
            payload["first_name"] = first_name
        if last_name:
            payload["last_name"] = last_name
        if email:
            payload["email"] = email

        try:
            response = self.client.patch(url, headers=self._get_headers(), json=payload)
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

    def delete_user(self, user_id: int) -> str:
        """
        Deletes a user from AWX.

        :param user_id: The ID of user to delete.
        :return: A JSON string containing deletion confirmation.
        """
        url = f"{self.mcp_server_url}/awx/users/{user_id}"
        try:
            response = self.client.delete(url, headers=self._get_headers())
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

    # Schedule Management
    def list_schedules(self, template_id: int) -> str:
        """
        Lists all schedules for a specific job template.

        :param template_id: The ID of job template to list schedules for.
        :return: A JSON string containing a list of schedules.
        """
        url = f"{self.mcp_server_url}/awx/job_templates/{template_id}/schedules"
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

    def get_schedule(self, schedule_id: int) -> str:
        """
        Retrieves details of a specific schedule.

        :param schedule_id: The ID of schedule to retrieve.
        :return: A JSON string containing schedule details.
        """
        url = f"{self.mcp_server_url}/awx/schedules/{schedule_id}"
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

    def create_schedule(self, template_id: int, name: str, rrule: str) -> str:
        """
        Creates a new schedule for a job template.

        :param template_id: The ID of job template to create schedule for.
        :param name: Name of the schedule.
        :param rrule: RRULE string defining the schedule recurrence.
        :return: A JSON string containing the created schedule details.
        """
        url = f"{self.mcp_server_url}/awx/job_templates/{template_id}/schedules"
        payload = {"name": name, "rrule": rrule}

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

    def update_schedule(
        self,
        schedule_id: int,
        name: Optional[str] = None,
        rrule: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> str:
        """
        Updates an existing schedule.

        :param schedule_id: The ID of schedule to update.
        :param name: Optional new name.
        :param rrule: Optional new RRULE string.
        :param enabled: Optional enabled/disabled status.
        :return: A JSON string containing the updated schedule details.
        """
        url = f"{self.mcp_server_url}/awx/schedules/{schedule_id}"
        payload = {}
        if name:
            payload["name"] = name
        if rrule:
            payload["rrule"] = rrule
        if enabled is not None:
            payload["enabled"] = enabled

        try:
            response = self.client.patch(url, headers=self._get_headers(), json=payload)
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

    def delete_schedule(self, schedule_id: int) -> str:
        """
        Deletes a schedule from AWX.

        :param schedule_id: The ID of schedule to delete.
        :return: A JSON string containing deletion confirmation.
        """
        url = f"{self.mcp_server_url}/awx/schedules/{schedule_id}"
        try:
            response = self.client.delete(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps({"status": "deleted", "id": schedule_id})
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})

    # Test Endpoint
    def test_connection(self) -> str:
        """
        Tests the connection to the AWX server.

        :return: A JSON string containing test results.
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

    def delete_inventory(self, inventory_id: int) -> str:
        """
        Deletes an inventory from AWX.

        :param inventory_id: The ID of inventory to delete.
        :return: A JSON string containing deletion confirmation.
        """
        url = f"{self.mcp_server_url}/awx/inventories/{inventory_id}"
        try:
            response = self.client.delete(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps({"status": "deleted", "id": inventory_id})
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_project(self, project_id: int) -> str:
        """
        Retrieves details of a specific project.

        :param project_id: The ID of project to retrieve.
        :return: A JSON string containing project details.
        """
        url = f"{self.mcp_server_url}/awx/projects/{project_id}"
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

    def update_project(
        self,
        project_id: int,
        name: Optional[str] = None,
        scm_type: Optional[str] = None,
        scm_url: Optional[str] = None,
        description: Optional[str] = None,
    ) -> str:
        """
        Updates an existing project in AWX.

        :param project_id: The ID of project to update.
        :param name: Optional new name.
        :param scm_type: Optional new SCM type.
        :param scm_url: Optional new SCM URL.
        :param description: Optional new description.
        :return: A JSON string containing the updated project details.
        """
        url = f"{self.mcp_server_url}/awx/projects/{project_id}"
        payload = {}
        if name:
            payload["name"] = name
        if scm_type:
            payload["scm_type"] = scm_type
        if scm_url:
            payload["scm_url"] = scm_url
        if description:
            payload["description"] = description

        try:
            response = self.client.patch(url, headers=self._get_headers(), json=payload)
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

    def delete_project(self, project_id: int) -> str:
        """
        Deletes a project from AWX.

        :param project_id: The ID of project to delete.
        :return: A JSON string containing deletion confirmation.
        """
        url = f"{self.mcp_server_url}/awx/projects/{project_id}"
        try:
            response = self.client.delete(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps({"status": "deleted", "id": project_id})
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_organization(self, organization_id: int) -> str:
        """
        Retrieves details of a specific organization.

        :param organization_id: The ID of organization to retrieve.
        :return: A JSON string containing organization details.
        """
        url = f"{self.mcp_server_url}/awx/organizations/{organization_id}"
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

    def update_organization(
        self,
        organization_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> str:
        """
        Updates an existing organization in AWX.

        :param organization_id: The ID of organization to update.
        :param name: Optional new name.
        :param description: Optional new description.
        :return: A JSON string containing the updated organization details.
        """
        url = f"{self.mcp_server_url}/awx/organizations/{organization_id}"
        payload = {}
        if name:
            payload["name"] = name
        if description:
            payload["description"] = description

        try:
            response = self.client.patch(url, headers=self._get_headers(), json=payload)
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

    def delete_organization(self, organization_id: int) -> str:
        """
        Deletes an organization from AWX.

        :param organization_id: The ID of organization to delete.
        :return: A JSON string containing deletion confirmation.
        """
        url = f"{self.mcp_server_url}/awx/organizations/{organization_id}"
        try:
            response = self.client.delete(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps({"status": "deleted", "id": organization_id})
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})

    # Activity Stream
    def list_activity_stream(self, page: int = 1, page_size: int = 20) -> str:
        """
        Lists activity stream events in AWX.

        :param page: The page number.
        :param page_size: The number of items per page.
        :return: A JSON string containing activity stream events.
        """
        url = f"{self.mcp_server_url}/awx/activity_stream?page={page}&page_size={page_size}"
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
