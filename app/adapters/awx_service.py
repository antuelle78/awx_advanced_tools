import httpx
from typing import Optional
from app.config import settings


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

    async def delete_schedule(self, schedule_id: int) -> dict:
        """Delete a schedule."""
        url = f"{self.base_url}/api/v2/schedules/{schedule_id}/"
        await self._request("DELETE", url)
        return {"status": "deleted", "id": schedule_id}

    async def list_templates(self) -> dict:
        """List all job templates."""
        url = f"{self.base_url}/api/v2/job_templates/"
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
    async def list_inventories(self) -> dict:
        """List all inventories."""
        url = f"{self.base_url}/api/v2/inventories/"
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

    async def list_organizations(self):
        url = f"{self.base_url}/api/v2/organizations/"

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
        url = f"{self.base_url}/api/v2/organizations/{organization_id}/"

        resp = await self._request("DELETE", url)

        return resp.json()

    # Projects methods

    async def list_projects(self):
        url = f"{self.base_url}/api/v2/projects/"

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
        url = f"{self.base_url}/api/v2/projects/{project_id}/"

        resp = await self._request("DELETE", url)

        return resp.json()

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
        url = f"{self.base_url}/api/v2/credentials/{credential_id}/"

        resp = await self._request("DELETE", url)

        return resp.json()

    # Users methods

    async def list_users(self):
        url = f"{self.base_url}/api/v2/users/"

        resp = await self._request("GET", url)

        return resp.json()

    async def get_user(self, user_id: int):
        url = f"{self.base_url}/api/v2/users/{user_id}/"

        resp = await self._request("GET", url)

        return resp.json()

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
        url = f"{self.base_url}/api/v2/users/{user_id}/"

        resp = await self._request("DELETE", url)

        return resp.json()

    # Workflow Job Templates methods

    async def list_workflow_job_templates(self):
        url = f"{self.base_url}/api/v2/workflow_job_templates/"

        resp = await self._request("GET", url)

        return resp.json()

    async def get_workflow_job_template(self, workflow_job_template_id: int):
        url = (
            f"{self.base_url}/api/v2/workflow_job_templates/{workflow_job_template_id}/"
        )

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
        url = (
            f"{self.base_url}/api/v2/workflow_job_templates/{workflow_job_template_id}/"
        )

        resp = await self._request("DELETE", url)

        return resp.json()

    async def launch_workflow_job_template(
        self, workflow_job_template_id: int, extra_vars: Optional[dict] = None
    ):
        url = f"{self.base_url}/api/v2/workflow_job_templates/{workflow_job_template_id}/launch/"

        payload = {}

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
        url = f"{self.base_url}/api/v2/notification_templates/{notification_id}/"

        resp = await self._request("DELETE", url)

        return resp.json()

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
        url = f"{self.base_url}/api/v2/instance_groups/{instance_group_id}/"

        resp = await self._request("DELETE", url)

        return resp.json()

    # Activity Stream methods

    async def list_activity_stream(self, page: int = 1, page_size: int = 20):
        url = (
            f"{self.base_url}/api/v2/activity_stream/?page={page}&page_size={page_size}"
        )

        resp = await self._request("GET", url)

        return resp.json()


# Singleton instance
awx_client = AWXClient()
