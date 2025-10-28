import httpx
import logging
from typing import Optional, Dict, Any
from app.config import settings
from fastapi import HTTPException


class AWXClient:
    """Service layer for interacting with Ansible Tower / AWX API."""

    def __init__(self) -> None:
        base_url = settings.awx_base_url
        if base_url is None:
            raise ValueError("AWX_BASE_URL must be set")
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        if base_url.endswith("/api/v2"):
            base_url = base_url[:-7]
        self.base_url = base_url
        self.auth = None
        if settings.awx_username and settings.awx_password:
            self.auth = (settings.awx_username, settings.awx_password)
        self.headers: dict[str, str] = {}

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient(auth=self.auth) as client:
            resp = await client.request(method, url, headers=self.headers, **kwargs)
            resp.raise_for_status()
            return resp

    async def launch_job_template(
        self, template_id: int, extra_vars: dict | None = None
    ) -> dict:
        """Launch an AWX job template."""
        url = f"{self.base_url}/api/v2/job_templates/{template_id}/launch/"
        payload: dict = {}
        if extra_vars:
            payload["extra_vars"] = extra_vars
        resp = await self._request("POST", url, json=payload)
        return resp.json()

    async def create_inventory(
        self, name: str, variables: dict | None = None, organization: int | None = None
    ) -> dict:
        """Create an inventory."""
        url = f"{self.base_url}/api/v2/inventories/"
        payload: dict = {"name": name}
        if variables:
            payload["variables"] = variables
        if organization:
            payload["organization"] = organization
        resp = await self._request("POST", url, json=payload)
        return resp.json()

    async def get_job(self, job_id: int) -> dict:
        """Retrieve a job by ID."""
        url = f"{self.base_url}/api/v2/jobs/{job_id}/"
        resp = await self._request("GET", url)
        return resp.json()

    async def list_schedules(self, template_id: int) -> dict:
        """List schedules for a job template."""
        url = f"{self.base_url}/api/v2/job_templates/{template_id}/schedules/"
        resp = await self._request("GET", url)
        return resp.json()

    async def toggle_schedule(self, schedule_id: int, enabled: bool) -> dict:
        """Enable or disable a schedule."""
        url = f"{self.base_url}/api/v2/schedules/{schedule_id}/"
        payload = {"enabled": enabled}
        resp = await self._request("PATCH", url, json=payload)
        return resp.json()

    async def update_schedule(
        self,
        schedule_id: int,
        name: Optional[str] = None,
        rrule: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> dict:
        """Update a schedule."""
        url = f"{self.base_url}/api/v2/schedules/{schedule_id}/"
        payload: Dict[str, Any] = {}
        if name:
            payload["name"] = name
        if rrule:
            payload["rrule"] = rrule
        if enabled is not None:
            payload["enabled"] = enabled
        resp = await self._request("PATCH", url, json=payload)
        return resp.json()

    async def delete_schedule(self, schedule_id: int) -> dict:
        """Delete a schedule."""
        url = f"{self.base_url}/api/v2/schedules/{schedule_id}/"
        await self._request("DELETE", url)
        return {"status": "deleted", "id": schedule_id}

    async def list_templates(self, name: Optional[str] = None) -> dict:
        """List all job templates, optionally filtered by name."""
        url = f"{self.base_url}/api/v2/job_templates/"
        if name:
            url += f"?name={name}"
        resp = await self._request("GET", url)
        return resp.json()

    async def list_jobs(self, page: int = 1) -> dict:
        """List jobs with pagination."""
        url = f"{self.base_url}/api/v2/jobs/"
        params = {"page": page}
        resp = await self._request("GET", url, params=params)
        return resp.json()

    async def get_schedule(self, schedule_id: int) -> dict:
        """Retrieve a schedule by ID."""
        url = f"{self.base_url}/api/v2/schedules/{schedule_id}/"
        resp = await self._request("GET", url)
        return resp.json()

    async def create_schedule(
        self, name: str, rrule: str, job_template_id: int
    ) -> dict:
        """Create a new schedule for a job template."""
        url = f"{self.base_url}/api/v2/job_templates/{job_template_id}/schedules/"
        payload = {
            "name": name,
            "rrule": rrule,
        }
        resp = await self._request("POST", url, json=payload)
        return resp.json()

    # NEW INVENTORY METHODS START
    async def list_inventories(self, name: Optional[str] = None) -> dict:
        """List all inventories, optionally filtered by name."""
        url = f"{self.base_url}/api/v2/inventories/"
        if name:
            url += f"?name={name}"
        resp = await self._request("GET", url)
        return resp.json()

    async def get_inventory(self, inventory_id: int) -> dict:
        """Retrieve details for an inventory."""
        url = f"{self.base_url}/api/v2/inventories/{inventory_id}/"
        resp = await self._request("GET", url)
        return resp.json()

    async def delete_inventory(self, inventory_id: int) -> dict:
        """Delete an inventory."""
        url = f"{self.base_url}/api/v2/inventories/{inventory_id}/"
        await self._request("DELETE", url)
        return {"status": "deleted", "id": inventory_id}

    async def sync_inventory(self, inventory_id: int) -> dict:
        """Trigger a sync of an inventory."""
        url = f"{self.base_url}/api/v2/inventories/{inventory_id}/sync/"
        resp = await self._request("POST", url)
        return resp.json()

    # NEW INVENTORY METHODS END

    # Organizations methods

    async def list_organizations(self, name: Optional[str] = None):
        """List all organizations, optionally filtered by name."""
        url = f"{self.base_url}/api/v2/organizations/"
        if name:
            url += f"?name={name}"
        resp = await self._request("GET", url)
        return resp.json()

    async def get_organization(self, organization_id: int):
        url = f"{self.base_url}/api/v2/organizations/{organization_id}/"

        resp = await self._request("GET", url)

        return resp.json()

    async def create_organization(self, name: str, description: Optional[str] = None):
        url = f"{self.base_url}/api/v2/organizations/"

        payload = {"name": name}

        if description:
            payload["description"] = description

        resp = await self._request("POST", url, json=payload)

        return resp.json()

    async def update_organization(
        self,
        organization_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        url = f"{self.base_url}/api/v2/organizations/{organization_id}/"

        payload = {}

        if name:
            payload["name"] = name

        if description:
            payload["description"] = description

        resp = await self._request("PATCH", url, json=payload)

        return resp.json()

    async def delete_organization(self, organization_id: int):
        """Delete an organization."""
        if not isinstance(organization_id, int) or organization_id <= 0:
            raise ValueError("organization_id must be a positive integer")

        url = f"{self.base_url}/api/v2/organizations/{organization_id}/"

        resp = await self._request("DELETE", url)

        # Handle empty response body gracefully (common for DELETE operations)
        try:
            return resp.json()
        except ValueError:  # JSON parsing error (empty response)
            return {"status": "deleted", "id": organization_id}

    # Projects methods

    async def list_projects(self, name: Optional[str] = None):
        """List all projects, optionally filtered by name."""
        url = f"{self.base_url}/api/v2/projects/"
        if name:
            url += f"?name={name}"
        resp = await self._request("GET", url)
        return resp.json()

    async def get_project(self, project_id: int):
        url = f"{self.base_url}/api/v2/projects/{project_id}/"

        resp = await self._request("GET", url)

        return resp.json()

    async def create_project(
        self, name: str, scm_type: str, scm_url: str, description: Optional[str] = None
    ):
        url = f"{self.base_url}/api/v2/projects/"

        payload = {"name": name, "scm_type": scm_type, "scm_url": scm_url}

        if description:
            payload["description"] = description

        resp = await self._request("POST", url, json=payload)

        return resp.json()

    async def update_project(
        self,
        project_id: int,
        name: Optional[str] = None,
        scm_type: Optional[str] = None,
        scm_url: Optional[str] = None,
        description: Optional[str] = None,
    ):
        url = f"{self.base_url}/api/v2/projects/{project_id}/"

        payload = {}

        if name:
            payload["name"] = name

        if scm_type:
            payload["scm_type"] = scm_type

        if scm_url:
            payload["scm_url"] = scm_url

        if description:
            payload["description"] = description

        resp = await self._request("PATCH", url, json=payload)

        return resp.json()

    async def delete_project(self, project_id: int):
        """Delete a project."""
        if not isinstance(project_id, int) or project_id <= 0:
            raise ValueError("project_id must be a positive integer")

        url = f"{self.base_url}/api/v2/projects/{project_id}/"

        try:
            resp = await self._request("DELETE", url)
            # Handle empty response body gracefully (common for DELETE operations)
            try:
                return resp.json()
            except ValueError:  # JSON parsing error (empty response)
                return {"status": "deleted", "id": project_id}
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 500:
                # AWX may return 500 even on successful delete
                return {"status": "deleted", "id": project_id}
            raise

    async def sync_project(self, project_id: int):
        url = f"{self.base_url}/api/v2/projects/{project_id}/update/"

        resp = await self._request("POST", url)

        return resp.json()

    # Credentials methods

    async def list_credentials(self):
        url = f"{self.base_url}/api/v2/credentials/"

        resp = await self._request("GET", url)

        return resp.json()

    async def get_credential(self, credential_id: int):
        url = f"{self.base_url}/api/v2/credentials/{credential_id}/"

        resp = await self._request("GET", url)

        return resp.json()

    async def create_credential(self, name: str, credential_type: int, inputs: dict):
        url = f"{self.base_url}/api/v2/credentials/"

        payload = {"name": name, "credential_type": credential_type, "inputs": inputs}

        resp = await self._request("POST", url, json=payload)

        return resp.json()

    async def update_credential(
        self,
        credential_id: int,
        name: Optional[str] = None,
        inputs: Optional[dict] = None,
    ):
        url = f"{self.base_url}/api/v2/credentials/{credential_id}/"

        payload: dict = {}

        if name:
            payload["name"] = name

        if inputs:
            payload["inputs"] = inputs

        resp = await self._request("PATCH", url, json=payload)

        return resp.json()

    async def delete_credential(self, credential_id: int):
        """Delete a credential."""
        if not isinstance(credential_id, int) or credential_id <= 0:
            raise ValueError("credential_id must be a positive integer")

        url = f"{self.base_url}/api/v2/credentials/{credential_id}/"

        resp = await self._request("DELETE", url)

        # Handle empty response body gracefully (common for DELETE operations)
        try:
            return resp.json()
        except ValueError:  # JSON parsing error (empty response)
            return {"status": "deleted", "id": credential_id}

    # Users methods

    async def list_users(self, username: Optional[str] = None):
        logging.info(f"DEBUG: list_users called with username = {username}")
        url = f"{self.base_url}/api/v2/users/"

        resp = await self._request("GET", url)

        users = resp.json()
        if username:
            users["results"] = [
                u for u in users.get("results", []) if u["username"] == username
            ]
            users["count"] = len(users["results"])
        return users

    async def get_user(self, user_id: int):
        url = f"{self.base_url}/api/v2/users/{user_id}/"

        resp = await self._request("GET", url)

        return resp.json()

    async def get_user_by_name(self, username: str):
        users = await self.list_users()
        for user in users.get("results", []):
            if user["username"] == username:
                return await self.get_user(user["id"])
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")

    async def create_user(
        self,
        username: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ):
        url = f"{self.base_url}/api/v2/users/"

        payload = {"username": username, "password": password}

        if first_name:
            payload["first_name"] = first_name

        if last_name:
            payload["last_name"] = last_name

        if email:
            payload["email"] = email

        resp = await self._request("POST", url, json=payload)

        return resp.json()

    async def update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ):
        url = f"{self.base_url}/api/v2/users/{user_id}/"

        payload = {}

        if username:
            payload["username"] = username

        if first_name:
            payload["first_name"] = first_name

        if last_name:
            payload["last_name"] = last_name

        if email:
            payload["email"] = email

        resp = await self._request("PATCH", url, json=payload)

        return resp.json()

    async def delete_user(self, user_id: int):
        """Delete a user from AWX."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("user_id must be a positive integer")

        url = f"{self.base_url}/api/v2/users/{user_id}/"

        resp = await self._request("DELETE", url)

        # Handle empty response body gracefully (common for DELETE operations)
        try:
            return resp.json()
        except ValueError:  # JSON parsing error (empty response)
            return {"status": "deleted", "id": user_id}

    # Workflow Job Templates methods

    def validate_host(self, host_data: dict) -> bool:
        """Validate host data."""
        required_fields = ["name", "inventory"]
        for field in required_fields:
            if field not in host_data:
                return False
        return True

    async def create_host(self, host_data: dict):
        """
        Create a new host with validation
        """
        # Validate against schema
        if not self.validate_host(host_data):
            raise ValueError("Invalid host data")

        url = f"{self.base_url}/api/v2/hosts/"
        resp = await self._request("POST", url, json=host_data)
        return resp.json()

    async def list_hosts(self, inventory: Optional[int] = None) -> dict:
        """List all hosts, optionally filtered by inventory."""
        url = f"{self.base_url}/api/v2/hosts/"
        if inventory:
            url += f"?inventory={inventory}"
        resp = await self._request("GET", url)
        return resp.json()

    async def create_job_template(
        self,
        name: str,
        inventory: int,
        project: int,
        playbook: str,
        description: Optional[str] = None,
        extra_vars: Optional[dict] = None,
    ):
        """Create a new job template."""
        url = f"{self.base_url}/api/v2/job_templates/"
        params = {
            "name": name,
            "inventory": inventory,
            "project": project,
            "playbook": playbook,
        }
        payload: Dict[str, Any] = {}
        if description:
            payload["description"] = description
        if extra_vars:
            payload["extra_vars"] = extra_vars
        if payload:
            resp = await self._request("POST", url, params=params, json=payload)
        else:
            resp = await self._request("POST", url, params=params)
        return resp.json()

    async def list_workflow_job_templates(self):
        url = f"{self.base_url}/api/v2/workflow_job_templates/"

        resp = await self._request("GET", url)

        return resp.json()

    async def create_workflow_job_template(
        self, name: str, description: Optional[str] = None
    ):
        url = f"{self.base_url}/api/v2/workflow_job_templates/"

        payload = {"name": name}

        if description:
            payload["description"] = description

        resp = await self._request("POST", url, json=payload)

        return resp.json()

    async def update_workflow_job_template(
        self,
        workflow_job_template_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        url = (
            f"{self.base_url}/api/v2/workflow_job_templates/{workflow_job_template_id}/"
        )

        payload = {}

        if name:
            payload["name"] = name

        if description:
            payload["description"] = description

        resp = await self._request("PATCH", url, json=payload)

        return resp.json()

    async def delete_workflow_job_template(self, workflow_job_template_id: int):
        """Delete a workflow job template."""
        if (
            not isinstance(workflow_job_template_id, int)
            or workflow_job_template_id <= 0
        ):
            raise ValueError("workflow_job_template_id must be a positive integer")

        url = (
            f"{self.base_url}/api/v2/workflow_job_templates/{workflow_job_template_id}/"
        )

        resp = await self._request("DELETE", url)

        # Handle empty response body gracefully (common for DELETE operations)
        try:
            return resp.json()
        except ValueError:  # JSON parsing error (empty response)
            return {"status": "deleted", "id": workflow_job_template_id}

    async def launch_workflow_job_template(
        self, workflow_job_template_id: int, extra_vars: Optional[Dict[str, Any]] = None
    ):
        url = f"{self.base_url}/api/v2/workflow_job_templates/{workflow_job_template_id}/launch/"

        payload: Dict[str, Any] = {}

        if extra_vars:
            payload["extra_vars"] = extra_vars

        resp = await self._request("POST", url, json=payload)

        return resp.json()

    # Notifications methods

    async def list_notifications(self):
        url = f"{self.base_url}/api/v2/notification_templates/"

        resp = await self._request("GET", url)

        return resp.json()

    async def get_notification(self, notification_id: int):
        url = f"{self.base_url}/api/v2/notification_templates/{notification_id}/"

        resp = await self._request("GET", url)

        return resp.json()

    async def create_notification(
        self, name: str, notification_type: str, notification_configuration: dict
    ):
        url = f"{self.base_url}/api/v2/notification_templates/"

        payload = {
            "name": name,
            "notification_type": notification_type,
            "notification_configuration": notification_configuration,
        }

        resp = await self._request("POST", url, json=payload)

        return resp.json()

    async def update_notification(
        self,
        notification_id: int,
        name: Optional[str] = None,
        notification_configuration: Optional[dict] = None,
    ):
        url = f"{self.base_url}/api/v2/notification_templates/{notification_id}/"

        payload: dict = {}

        if name:
            payload["name"] = name

        if notification_configuration:
            payload["notification_configuration"] = notification_configuration

        resp = await self._request("PATCH", url, json=payload)

        return resp.json()

    async def delete_notification(self, notification_id: int):
        """Delete a notification template."""
        if not isinstance(notification_id, int) or notification_id <= 0:
            raise ValueError("notification_id must be a positive integer")

        url = f"{self.base_url}/api/v2/notification_templates/{notification_id}/"

        resp = await self._request("DELETE", url)

        # Handle empty response body gracefully (common for DELETE operations)
        try:
            return resp.json()
        except ValueError:  # JSON parsing error (empty response)
            return {"status": "deleted", "id": notification_id}

    # Instance Groups methods

    async def list_instance_groups(self):
        url = f"{self.base_url}/api/v2/instance_groups/"

        resp = await self._request("GET", url)

        return resp.json()

    async def get_instance_group(self, instance_group_id: int):
        url = f"{self.base_url}/api/v2/instance_groups/{instance_group_id}/"

        resp = await self._request("GET", url)

        return resp.json()

    async def create_instance_group(
        self,
        name: str,
        policy_instance_percentage: Optional[int] = None,
        policy_instance_minimum: Optional[int] = None,
    ):
        url = f"{self.base_url}/api/v2/instance_groups/"

        payload: dict = {"name": name}

        if policy_instance_percentage:
            payload["policy_instance_percentage"] = policy_instance_percentage

        if policy_instance_minimum:
            payload["policy_instance_minimum"] = policy_instance_minimum

        resp = await self._request("POST", url, json=payload)

        return resp.json()

    async def update_instance_group(
        self,
        instance_group_id: int,
        name: Optional[str] = None,
        policy_instance_percentage: Optional[int] = None,
        policy_instance_minimum: Optional[int] = None,
    ):
        url = f"{self.base_url}/api/v2/instance_groups/{instance_group_id}/"

        payload: dict = {}

        if name:
            payload["name"] = name

        if policy_instance_percentage:
            payload["policy_instance_percentage"] = policy_instance_percentage

        if policy_instance_minimum:
            payload["policy_instance_minimum"] = policy_instance_minimum

        resp = await self._request("PATCH", url, json=payload)

        return resp.json()

    async def delete_instance_group(self, instance_group_id: int):
        """Delete an instance group."""
        if not isinstance(instance_group_id, int) or instance_group_id <= 0:
            raise ValueError("instance_group_id must be a positive integer")

        url = f"{self.base_url}/api/v2/instance_groups/{instance_group_id}/"

        resp = await self._request("DELETE", url)

        # Handle empty response body gracefully (common for DELETE operations)
        try:
            return resp.json()
        except ValueError:  # JSON parsing error (empty response)
            return {"status": "deleted", "id": instance_group_id}

    # Activity Stream methods

    async def list_activity_stream(self, page: int = 1, page_size: int = 20):
        url = (
            f"{self.base_url}/api/v2/activity_stream/?page={page}&page_size={page_size}"
        )

        resp = await self._request("GET", url)

        return resp.json()


# Singleton instance
awx_client = AWXClient()
