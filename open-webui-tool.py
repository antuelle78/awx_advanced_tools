"""
title: 'Ansible AWX Controller'
author: 'Your Name'
description: 'A tool to interact with Ansible AWX through the MCP Server.'
requirements:
  - 'httpx'
"""

import httpx
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import json
import logging
import time
import os


class PromptOptimizer:
    """Optimizes prompts for better LLM tool usage success rate."""

    def __init__(self):
        self.tool_prompts = self._load_tool_prompts()
        self.confidence_threshold = 0.8
        self.log_file = "tool_usage.log"

    def _load_tool_prompts(self) -> Dict[str, str]:
        """Load optimized prompts for each tool."""
        return {
            "list_templates": "List all available job templates in AWX. Use this to see what automation jobs are available.",
            "launch_job_template": "Launch a specific job template in AWX. Provide the template_id and any extra_vars as a JSON object.",
            "list_jobs": "List all jobs in AWX. Optionally provide a page number for pagination.",
            "get_job": "Get the status of a specific job in AWX. Provide the job_id.",
            "list_inventories": "List all inventories in AWX.",
            "create_inventory": "Create a new inventory in AWX. Provide name, organization, and variables.",
            "get_inventory": "Get details of a specific inventory in AWX. Provide the inventory_id.",
            "delete_inventory": "Delete an inventory in AWX. Provide the inventory_id.",
            "sync_inventory": "Sync an inventory in AWX. Provide the inventory_id.",
            "list_schedules": "List schedules for a job template in AWX. Provide the template_id.",
            "get_schedule": "Get details of a schedule in AWX. Provide the schedule_id.",
            "create_schedule": "Create a schedule for a job template in AWX. Provide name, rrule, and job_template_id.",
            "toggle_schedule": "Enable or disable a schedule in AWX. Provide schedule_id and enabled status.",
            "delete_schedule": "Delete a schedule in AWX. Provide the schedule_id.",
            "list_organizations": "List all organizations in AWX.",
            "get_organization": "Get details of an organization in AWX. Provide the organization_id.",
            "create_organization": "Create a new organization in AWX. Provide name and description.",
            "update_organization": "Update an organization in AWX. Provide organization_id, name, and description.",
            "delete_organization": "Delete an organization in AWX. Provide the organization_id.",
            "list_projects": "List all projects in AWX.",
            "get_project": "Get details of a project in AWX. Provide the project_id.",
            "create_project": "Create a new project in AWX. Provide name, scm_type, scm_url, and description.",
            "update_project": "Update a project in AWX. Provide project_id and other parameters.",
            "delete_project": "Delete a project in AWX. Provide the project_id.",
            "sync_project": "Sync a project in AWX. Provide the project_id.",
            "list_credentials": "List all credentials in AWX.",
            "get_credential": "Get details of a credential in AWX. Provide the credential_id.",
            "create_credential": "Create a new credential in AWX. Provide name, credential_type, and inputs.",
            "update_credential": "Update a credential in AWX. Provide credential_id and other parameters.",
            "delete_credential": "Delete a credential in AWX. Provide the credential_id.",
            "list_users": "List all users in AWX.",
            "get_user": "Get details of a user in AWX. Provide the user_id.",
            "create_user": "Create a new user in AWX. Provide username, password, and other parameters.",
            "update_user": "Update a user in AWX. Provide user_id and other parameters.",
            "delete_user": "Delete a user in AWX. Provide the user_id.",
            "list_workflow_job_templates": "List all workflow job templates in AWX.",
            "get_workflow_job_template": "Get details of a workflow job template in AWX. Provide the workflow_job_template_id.",
            "create_workflow_job_template": "Create a new workflow job template in AWX. Provide name and description.",
            "update_workflow_job_template": "Update a workflow job template in AWX. Provide workflow_job_template_id and other parameters.",
            "delete_workflow_job_template": "Delete a workflow job template in AWX. Provide the workflow_job_template_id.",
            "launch_workflow_job_template": "Launch a workflow job template in AWX. Provide workflow_job_template_id and extra_vars.",
            "list_notifications": "List all notification templates in AWX.",
            "get_notification": "Get details of a notification template in AWX. Provide the notification_id.",
            "create_notification": "Create a new notification template in AWX. Provide name, notification_type, and notification_configuration.",
            "update_notification": "Update a notification template in AWX. Provide notification_id and other parameters.",
            "delete_notification": "Delete a notification template in AWX. Provide the notification_id.",
            "list_instance_groups": "List all instance groups in AWX.",
            "get_instance_group": "Get details of an instance group in AWX. Provide the instance_group_id.",
            "create_instance_group": "Create a new instance group in AWX. Provide name and other parameters.",
            "update_instance_group": "Update an instance group in AWX. Provide instance_group_id and other parameters.",
            "delete_instance_group": "Delete an instance group in AWX. Provide the instance_group_id.",
            "list_activity_stream": "List activity stream events in AWX. Provide page and page_size.",
        }

    def get_optimized_prompt(self, tool_name: str, **kwargs) -> str:
        """Generate an optimized prompt for a specific tool."""
        base_prompt = self.tool_prompts.get(
            tool_name, "Use this tool to interact with AWX."
        )
        confidence_cues = [
            "I am confident this is the correct tool.",
            "This tool call should succeed.",
            "Using the appropriate AWX API endpoint.",
        ]
        cue = confidence_cues[hash(tool_name) % len(confidence_cues)]
        return f"{cue} {base_prompt}"

    def log_tool_usage(self, tool_name: str, success: bool, response_time: float):
        """Log tool usage for feedback loop."""
        log_entry = {
            "tool": tool_name,
            "success": success,
            "response_time": response_time,
            "timestamp": time.time(),
        }
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logging.warning(f"Failed to log tool usage: {e}")


class Tools:
    class Valves(BaseModel):
        mcp_server_url: str = Field(
            default="http://localhost:8001", description="The base URL of MCP server."
        )

    def __init__(self):
        self.valves = self.Valves()
        self.client = httpx.Client(timeout=30.0)  # Add timeout for requests
        self.prompt_optimizer = PromptOptimizer()

    def _get_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def get_optimized_prompt(self, tool_name: str, **kwargs) -> str:
        """Get an optimized prompt for a specific tool."""
        return self.prompt_optimizer.get_optimized_prompt(tool_name, **kwargs)

    def log_tool_usage(self, tool_name: str, success: bool, response_time: float):
        """Log tool usage for feedback loop."""
        self.prompt_optimizer.log_tool_usage(tool_name, success, response_time)

    def get_all_optimized_prompts(self) -> Dict[str, str]:
        """Get optimized prompts for all available tools."""
        return self.prompt_optimizer.tool_prompts

    @property
    def mcp_server_url(self) -> str:
        return self.valves.mcp_server_url

    def list_templates(self) -> str:
        """
        Lists all job templates in AWX.

        :return: A JSON string containing a list of users and their details.

        """
        start_time = time.time()
        url = f"{self.mcp_server_url}/awx/templates"

        try:
            response = self.client.get(url, headers=self._get_headers())

            response.raise_for_status()

            self.log_tool_usage("list_templates", True, time.time() - start_time)
            return json.dumps(response.json())

        except httpx.HTTPStatusError as e:
            self.log_tool_usage("list_templates", False, time.time() - start_time)
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )

        except Exception as e:
            self.log_tool_usage("list_templates", False, time.time() - start_time)
            return json.dumps({"error": str(e)})

    def launch_job_template(
        self, template_id: int, extra_vars: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Launches an AWX job template to start a new job.

        :param template_id: The ID of job template to launch.
        :param extra_vars: A dictionary of extra variables to pass to job.
        :return: A JSON string containing details of newly created job, including its 'id'. This 'id' should be used with 'get_job' tool to check job's status.
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

    def create_inventory(
        self, name: str, organization: int, variables: Optional[dict] = None
    ) -> str:
        """
        Creates a new inventory in AWX.

        :param name: The name of inventory.
        :param organization: The ID of organization for inventory.
        :param variables: A dictionary of variables for inventory.
        :return: The result of create inventory action.
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

    def list_jobs(self, page: int = 1) -> str:
        """
        Lists all jobs in AWX with pagination.

        :param page: The page number to retrieve (default: 1).
        :return: A JSON string containing a list of jobs and their details.
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

    def get_job(self, job_id: int) -> str:
        """
        Retrieves current status and details of a specific job, such as one started by 'launch_job_template'.

        :param job_id: The ID of job to retrieve. This is the 'id' returned by 'launch_job_template' tool.
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

    def list_schedules(self, template_id: int) -> str:
        """
        Lists all schedules associated with a specific job template.

        :param template_id: The ID of job template to query.
        :return: A JSON string containing a list of schedules and their details.
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
        :return: A JSON string containing details of schedule.
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

    def toggle_schedule(self, schedule_id: int, enabled: bool) -> str:
        """
        Enables or disables a specific job schedule.

        :param schedule_id: The ID of schedule to modify. Use list_schedules to find this ID.
        :param enabled: Set to true to enable schedule, or false to disable it.
        :return: A JSON string with updated schedule details.
        """
        url = f"{self.mcp_server_url}/awx/schedules/{schedule_id}"
        payload = {"enabled": enabled}
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
        Permanently deletes a job schedule.

        :param schedule_id: The ID of schedule to delete.
        :return: A confirmation message indicating success or failure.
        """
        url = f"{self.mcp_server_url}/awx/schedules/{schedule_id}"
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

    def create_schedule(self, name: str, rrule: str, job_template_id: int) -> str:
        """
        Creates a new schedule for a job template.

        :param name: The name of schedule.
        :param rrule: The recurrence rule for schedule (e.g., 'DTSTART:20251024T120000Z RRULE:FREQ=DAILY;INTERVAL=1').
        :param job_template_id: The ID of job template to schedule.
        :return: A JSON string with details of newly created schedule.
        """
        url = f"{self.mcp_server_url}/awx/job_templates/{job_template_id}/schedules"
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

    def list_inventories(self) -> str:
        """
        Lists all inventories in AWX.

        :return: A JSON string containing a list of inventories and their details.
        """
        url = f"{self.mcp_server_url}/awx/inventories"
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

    def get_inventory(self, inventory_id: int) -> str:
        """
        Retrieves details of a specific inventory.

        :param inventory_id: The ID of inventory to retrieve.
        :return: A JSON string containing details of inventory.
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

    def delete_inventory(self, inventory_id: int) -> str:
        """
        Permanently deletes an inventory.

        :param inventory_id: The ID of inventory to delete.
        :return: A confirmation message indicating success or failure.
        """
        url = f"{self.mcp_server_url}/awx/inventories/{inventory_id}"
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

    def sync_inventory(self, inventory_id: int) -> str:
        """
        Triggers a sync of an inventory.

        :param inventory_id: The ID of inventory to sync.
        :return: A JSON string with details of sync job.
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

    def list_organizations(self) -> str:
        """
        Lists all organizations in AWX.

        :return: A JSON string containing a list of organizations and their details.
        """
        url = f"{self.mcp_server_url}/awx/organizations"
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

    def get_organization(self, organization_id: int) -> str:
        """
        Retrieves details of a specific organization.

        :param organization_id: The ID of organization to retrieve.
        :return: A JSON string containing details of organization.
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

    def create_organization(self, name: str, description: Optional[str] = None) -> str:
        """
        Creates a new organization in AWX.

        :param name: The name of organization.
        :param description: The description of organization.
        :return: The result of create organization action.
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

    def update_organization(
        self,
        organization_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> str:
        """
        Updates an organization in AWX.

        :param organization_id: The ID of organization to update.
        :param name: The new name of organization.
        :param description: The new description of organization.
        :return: The result of update organization action.
        """
        url = f"{self.mcp_server_url}/awx/organizations/{organization_id}"
        payload: Dict[str, Any] = {}
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
        Deletes an organization in AWX.

        :param organization_id: The ID of organization to delete.

        :return: A confirmation message indicating success or failure.

        """
        url = f"{self.mcp_server_url}/awx/organizations/{organization_id}"

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

    def list_projects(self) -> str:
        """
        Lists all projects in AWX.

        :return: A JSON string containing a list of projects and their details.

        """
        url = f"{self.mcp_server_url}/awx/projects"

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

    def get_project(self, project_id: int) -> str:
        """
        Retrieves details of a specific project.

        :param project_id: The ID of project to retrieve.

        :return: A JSON string containing details of project.

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

    def create_project(
        self, name: str, scm_type: str, scm_url: str, description: Optional[str] = None
    ) -> str:
        """
        Creates a new project in AWX.

        :param name: The name of project.

        :param scm_type: The type of SCM (e.g., git).

        :param scm_url: The URL of SCM repository.

        :param description: The description of project.

        :return: The result of create project action.

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

    def update_project(
        self,
        project_id: int,
        name: Optional[str] = None,
        scm_type: Optional[str] = None,
        scm_url: Optional[str] = None,
        description: Optional[str] = None,
    ) -> str:
        """
        Updates a project in AWX.

        :param project_id: The ID of project to update.

        :param name: The new name of project.

        :param scm_type: The new SCM type.

        :param scm_url: The new SCM URL.

        :param description: The new description of project.

        :return: The result of update project action.

        """
        url = f"{self.mcp_server_url}/awx/projects/{project_id}"

        payload: Dict[str, Any] = {}

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
        Deletes a project in AWX.

        :param project_id: The ID of project to delete.

        :return: A confirmation message indicating success or failure.

        """
        url = f"{self.mcp_server_url}/awx/projects/{project_id}"

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

    def sync_project(self, project_id: int) -> str:
        """
        Triggers a sync of a project in AWX.

        :param project_id: The ID of project to sync.

        :return: A JSON string with details of sync job.

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

    def list_credentials(self) -> str:
        """
        Lists all credentials in AWX.

        :return: A JSON string containing a list of credentials and their details.

        """
        url = f"{self.mcp_server_url}/awx/credentials"

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

    def get_credential(self, credential_id: int) -> str:
        """
        Retrieves details of a specific credential.

        :param credential_id: The ID of credential to retrieve.

        :return: A JSON string containing details of credential.

        """
        url = f"{self.mcp_server_url}/awx/credentials/{credential_id}"

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

    def create_credential(self, name: str, credential_type: int, inputs: dict) -> str:
        """
        Creates a new credential in AWX.

        :param name: The name of credential.

        :param credential_type: The ID of credential type.

        :param inputs: A dictionary of inputs for credential.

        :return: The result of create credential action.

        """
        url = f"{self.mcp_server_url}/awx/credentials"

        payload = {"name": name, "credential_type": credential_type, "inputs": inputs}

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

    def update_credential(
        self,
        credential_id: int,
        name: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Updates a credential in AWX.

        :param credential_id: The ID of credential to update.

        :param name: The new name of credential.

        :param inputs: The new inputs for credential.

        :return: The result of update credential action.

        """
        url = f"{self.mcp_server_url}/awx/credentials/{credential_id}"

        payload: Dict[str, Any] = {}

        if name:
            payload["name"] = name

        if inputs:
            payload["inputs"] = inputs

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

    def delete_credential(self, credential_id: int) -> str:
        """
        Deletes a credential in AWX.

        :param credential_id: The ID of credential to delete.

        :return: A confirmation message indicating success or failure.

        """
        url = f"{self.mcp_server_url}/awx/credentials/{credential_id}"

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

    def list_users(self) -> str:
        """
        Lists all users in AWX.

        :return: A JSON string containing a list of users and their details.

        """
        url = f"{self.mcp_server_url}/awx/users?current_=1"

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

    def get_user(self, user_id: int) -> str:
        """
        Retrieves details of a specific user.

        :param user_id: The ID of user to retrieve.

        :return: A JSON string containing details of user.

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

        :param username: The username of user.

        :param password: The password of user.

        :param first_name: The first name of user.

        :param last_name: The last name of user.

        :param email: The email of user.

        :return: The result of create user action.

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

    def update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> str:
        """
        Updates a user in AWX.

        :param user_id: The ID of user to update.

        :param username: The new username of user.

        :param first_name: The new first name of user.

        :param last_name: The new last name of user.

        :param email: The new email of user.

        :return: The result of update user action.

        """
        url = f"{self.mcp_server_url}/awx/users/{user_id}"

        payload: Dict[str, Any] = {}

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
        Deletes a user in AWX.

        :param user_id: The ID of user to delete.

        :return: A confirmation message indicating success or failure.

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

    def list_workflow_job_templates(self) -> str:
        """
        Lists all workflow job templates in AWX.

        :return: A JSON string containing a list of workflow job templates and their details.

        """
        url = f"{self.mcp_server_url}/awx/workflow_job_templates"

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

    def get_workflow_job_template(self, workflow_job_template_id: int) -> str:
        """
        Retrieves details of a specific workflow job template.

        :param workflow_job_template_id: The ID of workflow job template to retrieve.

        :return: A JSON string containing details of workflow job template.

        """
        url = f"{self.mcp_server_url}/awx/workflow_job_templates/{workflow_job_template_id}"

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

    def create_workflow_job_template(
        self, name: str, description: Optional[str] = None
    ) -> str:
        """
        Creates a new workflow job template in AWX.

        :param name: The name of workflow job template.

        :param description: The description of workflow job template.

        :return: The result of create workflow job template action.

        """
        url = f"{self.mcp_server_url}/awx/workflow_job_templates"

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

    def update_workflow_job_template(
        self,
        workflow_job_template_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> str:
        """
        Updates a workflow job template in AWX.

        :param workflow_job_template_id: The ID of workflow job template to update.

        :param name: The new name of workflow job template.

        :param description: The new description of workflow job template.

        :return: The result of update workflow job template action.

        """
        url = f"{self.mcp_server_url}/awx/workflow_job_templates/{workflow_job_template_id}"

        payload: Dict[str, Any] = {}

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

    def delete_workflow_job_template(self, workflow_job_template_id: int) -> str:
        """
        Deletes a workflow job template in AWX.

        :param workflow_job_template_id: The ID of workflow job template to delete.

        :return: A confirmation message indicating success or failure.

        """
        url = f"{self.mcp_server_url}/awx/workflow_job_templates/{workflow_job_template_id}"

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

    def launch_workflow_job_template(
        self, workflow_job_template_id: int, extra_vars: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Launches a workflow job template in AWX.

        :param workflow_job_template_id: The ID of workflow job template to launch.

        :param extra_vars: A dictionary of extra variables to pass to workflow job.

        :return: The result of launch workflow job template action.

        """
        url = f"{self.mcp_server_url}/awx/workflow_job_templates/{workflow_job_template_id}/launch"

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

    def list_notifications(self) -> str:
        """
        Lists all notifications in AWX.

        :return: A JSON string containing a list of notifications and their details.

        """
        url = f"{self.mcp_server_url}/awx/notifications"

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

    def get_notification(self, notification_id: int) -> str:
        """
        Retrieves details of a specific notification.

        :param notification_id: The ID of notification to retrieve.

        :return: A JSON string containing details of notification.

        """
        url = f"{self.mcp_server_url}/awx/notifications/{notification_id}"

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

    def create_notification(
        self, name: str, notification_type: str, notification_configuration: dict
    ) -> str:
        """
        Creates a new notification in AWX.

        :param name: The name of notification.

        :param notification_type: The type of notification.

        :param notification_configuration: The configuration for notification.

        :return: The result of create notification action.

        """
        url = f"{self.mcp_server_url}/awx/notifications"

        payload = {
            "name": name,
            "notification_type": notification_type,
            "notification_configuration": notification_configuration,
        }

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

    def update_notification(
        self,
        notification_id: int,
        name: Optional[str] = None,
        notification_configuration: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Updates a notification in AWX.

        :param notification_id: The ID of notification to update.

        :param name: The new name of notification.

        :param notification_configuration: The new configuration for notification.

        :return: The result of update notification action.

        """
        url = f"{self.mcp_server_url}/awx/notifications/{notification_id}"

        payload: Dict[str, Any] = {}

        if name:
            payload["name"] = name

        if notification_configuration:
            payload["notification_configuration"] = notification_configuration

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

    def delete_notification(self, notification_id: int) -> str:
        """
        Deletes a notification in AWX.

        :param notification_id: The ID of notification to delete.

        :return: A confirmation message indicating success or failure.

        """
        url = f"{self.mcp_server_url}/awx/notifications/{notification_id}"

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

    def list_instance_groups(self) -> str:
        """
        Lists all instance groups in AWX.

        :return: A JSON string containing a list of instance groups and their details.

        """
        url = f"{self.mcp_server_url}/awx/instance_groups"

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

    def get_instance_group(self, instance_group_id: int) -> str:
        """
        Retrieves details of a specific instance group.

        :param instance_group_id: The ID of instance group to retrieve.

        :return: A JSON string containing details of instance group.

        """
        url = f"{self.mcp_server_url}/awx/instance_groups/{instance_group_id}"

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

    def create_instance_group(
        self,
        name: str,
        policy_instance_percentage: Optional[int] = None,
        policy_instance_minimum: Optional[int] = None,
    ) -> str:
        """
        Creates a new instance group in AWX.

        :param name: The name of instance group.

        :param policy_instance_percentage: The policy instance percentage.

        :param policy_instance_minimum: The policy instance minimum.

        :return: The result of create instance group action.

        """
        url = f"{self.mcp_server_url}/awx/instance_groups"

        payload: Dict[str, Any] = {"name": name}

        if policy_instance_percentage:
            payload["policy_instance_percentage"] = policy_instance_percentage

        if policy_instance_minimum:
            payload["policy_instance_minimum"] = policy_instance_minimum

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

    def update_instance_group(
        self,
        instance_group_id: int,
        name: Optional[str] = None,
        policy_instance_percentage: Optional[int] = None,
        policy_instance_minimum: Optional[int] = None,
    ) -> str:
        """
        Updates an instance group in AWX.

        :param instance_group_id: The ID of instance group to update.

        :param name: The new name of instance group.

        :param policy_instance_percentage: The new policy instance percentage.

        :param policy_instance_minimum: The new policy instance minimum.

        :return: The result of update instance group action.

        """
        url = f"{self.mcp_server_url}/awx/instance_groups/{instance_group_id}"

        payload: Dict[str, Any] = {}

        if name:
            payload["name"] = name

        if policy_instance_percentage:
            payload["policy_instance_percentage"] = policy_instance_percentage

        if policy_instance_minimum:
            payload["policy_instance_minimum"] = policy_instance_minimum

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

    def delete_instance_group(self, instance_group_id: int) -> str:
        """
        Deletes an instance group in AWX.

        :param instance_group_id: The ID of instance group to delete.

        :return: A confirmation message indicating success or failure.

        """
        url = f"{self.mcp_server_url}/awx/instance_groups/{instance_group_id}"

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

    def list_activity_stream(self, page: int = 1, page_size: int = 20) -> str:
        """
        Lists activity stream in AWX.

        :param page: The page number.

        :param page_size: The number of items per page.

        :return: A JSON string containing activity stream.

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
