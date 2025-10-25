"""
title: 'Ansible AWX Controller'
author: 'Your Name'
description: 'A tool to interact with Ansible AWX through the MCP Server.'
requirements:
  - 'httpx'
"""

import os
import httpx
from pydantic import BaseModel, Field
import json

class Tools:
    class Valves(BaseModel):
        jwt_token: str = Field(
            default="",
            description="The JWT token for authenticating with the MCP server."
        )

    def __init__(self):
        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://host.docker.internal:8001")
        self.valves = self.Valves()
        self.client = httpx.Client()

    def _get_headers(self) -> dict:
        if not self.valves.jwt_token:
            raise ValueError("JWT Token is not configured in the tool's valves.")
        return {
            "Authorization": f"Bearer {self.valves.jwt_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def launch_job_template(self, template_id: int, extra_vars: dict = None) -> str:
        """
        Launches an AWX job template to start a new job.

        :param template_id: The ID of the job template to launch.
        :param extra_vars: A dictionary of extra variables to pass to the job.
        :return: A JSON string containing the details of the newly created job, including its 'id'. This 'id' should be used with the 'get_job' tool to check the job's status.
        """
        url = f"{self.mcp_server_url}/awx/job_templates/{template_id}/launch"
        payload = {}
        if extra_vars:
            payload['extra_vars'] = extra_vars

        try:
            response = self.client.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps({"error": f"HTTP error occurred: {e.response.status_code}", "detail": e.response.text})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def create_inventory(self, name: str, organization: int, variables: dict = None) -> str:
        """
        Creates a new inventory in AWX.

        :param name: The name of the inventory.
        :param organization: The ID of the organization for the inventory.
        :param variables: A dictionary of variables for the inventory.
        :return: The result of the create inventory action.
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
            return json.dumps({"error": f"HTTP error occurred: {e.response.status_code}", "detail": e.response.text})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_job(self, job_id: int) -> str:
        """
        Retrieves the current status and details of a specific job, such as one started by 'launch_job_template'.

        :param job_id: The ID of the job to retrieve. This is the 'id' returned by the 'launch_job_template' tool.
        :return: A JSON string containing the status and details of the job.
        """
        url = f"{self.mcp_server_url}/awx/jobs/{job_id}"
        try:
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps({"error": f"HTTP error occurred: {e.response.status_code}", "detail": e.response.text})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def list_schedules(self, template_id: int) -> str:
        """
        Lists all schedules associated with a specific job template.

        :param template_id: The ID of the job template to query.
        :return: A JSON string containing a list of schedules and their details.
        """
        url = f"{self.mcp_server_url}/awx/job_templates/{template_id}/schedules"
        try:
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps({"error": f"HTTP error occurred: {e.response.status_code}", "detail": e.response.text})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def toggle_schedule(self, schedule_id: int, enabled: bool) -> str:
        """
        Enables or disables a specific job schedule.

        :param schedule_id: The ID of the schedule to modify. Use list_schedules to find this ID.
        :param enabled: Set to true to enable the schedule, or false to disable it.
        :return: A JSON string with the updated schedule details.
        """
        url = f"{self.mcp_server_url}/awx/schedules/{schedule_id}"
        payload = {"enabled": enabled}
        try:
            response = self.client.patch(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps({"error": f"HTTP error occurred: {e.response.status_code}", "detail": e.response.text})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def delete_schedule(self, schedule_id: int) -> str:
        """
        Permanently deletes a job schedule.

        :param schedule_id: The ID of the schedule to delete.
        :return: A confirmation message indicating success or failure.
        """
        url = f"{self.mcp_server_url}/awx/schedules/{schedule_id}"
        try:
            response = self.client.delete(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps({"error": f"HTTP error occurred: {e.response.status_code}", "detail": e.response.text})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def create_schedule(self, name: str, rrule: str, job_template_id: int) -> str:
        """
        Creates a new schedule for a job template.

        :param name: The name of the schedule.
        :param rrule: The recurrence rule for the schedule (e.g., 'DTSTART:20251024T120000Z RRULE:FREQ=DAILY;INTERVAL=1').
        :param job_template_id: The ID of the job template to schedule.
        :return: A JSON string with the details of the newly created schedule.
        """
        url = f"{self.mcp_server_url}/awx/job_templates/{job_template_id}/schedules"
        payload = {
            "name": name,
            "rrule": rrule
        }
        try:
            response = self.client.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps({"error": f"HTTP error occurred: {e.response.status_code}", "detail": e.response.text})
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
            return json.dumps({"error": f"HTTP error occurred: {e.response.status_code}", "detail": e.response.text})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_inventory(self, inventory_id: int) -> str:
        """
        Retrieves the details of a specific inventory.

        :param inventory_id: The ID of the inventory to retrieve.
        :return: A JSON string containing the details of the inventory.
        """
        url = f"{self.mcp_server_url}/awx/inventories/{inventory_id}"
        try:
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps({"error": f"HTTP error occurred: {e.response.status_code}", "detail": e.response.text})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def delete_inventory(self, inventory_id: int) -> str:
        """
        Permanently deletes an inventory.

        :param inventory_id: The ID of the inventory to delete.
        :return: A confirmation message indicating success or failure.
        """
        url = f"{self.mcp_server_url}/awx/inventories/{inventory_id}"
        try:
            response = self.client.delete(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps({"error": f"HTTP error occurred: {e.response.status_code}", "detail": e.response.text})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def sync_inventory(self, inventory_id: int) -> str:
        """
        Triggers a sync of an inventory.

        :param inventory_id: The ID of the inventory to sync.
        :return: A JSON string with the details of the sync job.
        """
        url = f"{self.mcp_server_url}/awx/inventories/{inventory_id}/sync"
        try:
            response = self.client.post(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps(response.json())
        except httpx.HTTPStatusError as e:
            return json.dumps({"error": f"HTTP error occurred: {e.response.status_code}", "detail": e.response.text})
        except Exception as e:
            return json.dumps({"error": str(e)})

tools = Tools()
