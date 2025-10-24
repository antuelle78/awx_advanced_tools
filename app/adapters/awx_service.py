import httpx
from app.config import settings

class AWXClient:
    """Service layer for interacting with Ansible Tower / AWX API."""

    def __init__(self) -> None:
        base_url = settings.awx_base_url
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        if base_url.endswith('/api/v2'):
            base_url = base_url[:-7]
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {settings.awx_token}"}

    async def launch_job_template(self, template_id: int, extra_vars: dict | None = None) -> dict:
        """Launch an AWX job template."""
        url = f"{self.base_url}/api/v2/job_templates/{template_id}/launch/"
        payload: dict = {}
        if extra_vars:
            payload["extra_vars"] = extra_vars
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def create_inventory(self, name: str, variables: dict | None = None, organization: int | None = None) -> dict:
        """Create an inventory."""
        url = f"{self.base_url}/api/v2/inventories/"
        payload: dict = {"name": name}
        if variables:
            payload["variables"] = variables
        if organization:
            payload["organization"] = organization
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def get_job(self, job_id: int) -> dict:
        """Retrieve a job by ID."""
        url = f"{self.base_url}/api/v2/jobs/{job_id}/"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def list_schedules(self, template_id: int) -> dict:
        """List schedules for a job template."""
        url = f"{self.base_url}/api/v2/job_templates/{template_id}/schedules/"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def toggle_schedule(self, schedule_id: int, enabled: bool) -> dict:
        """Enable or disable a schedule."""
        url = f"{self.base_url}/api/v2/schedules/{schedule_id}/"
        payload = {"enabled": enabled}
        async with httpx.AsyncClient() as client:
            resp = await client.patch(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def delete_schedule(self, schedule_id: int) -> dict:
        """Delete a schedule."""
        url = f"{self.base_url}/api/v2/schedules/{schedule_id}/"
        async with httpx.AsyncClient() as client:
            resp = await client.delete(url, headers=self.headers)
            resp.raise_for_status()
            return {"status": "deleted", "id": schedule_id}

    async def list_templates(self) -> dict:
        """List all job templates."""
        url = f"{self.base_url}/api/v2/job_templates/"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def list_jobs(self, page: int = 1) -> dict:
        """List jobs with pagination."""
        url = f"{self.base_url}/api/v2/jobs/"
        params = {"page": page}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def get_schedule(self, schedule_id: int) -> dict:
        """Retrieve a schedule by ID."""
        url = f"{self.base_url}/api/v2/schedules/{schedule_id}/"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def create_schedule(self, name: str, rrule: str, job_template_id: int) -> dict:
        """Create a new schedule for a job template."""

        # removed duplicate create_schedule payload


        # removed duplicate create_schedule payload

    # NEW INVENTORY METHODS START
    async def list_inventories(self) -> dict:
        """List all inventories."""
        url = f"{self.base_url}/api/v2/inventories/"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def get_inventory(self, inventory_id: int) -> dict:
        """Retrieve details for an inventory."""
        url = f"{self.base_url}/api/v2/inventories/{inventory_id}/"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def delete_inventory(self, inventory_id: int) -> dict:
        """Delete an inventory."""
        url = f"{self.base_url}/api/v2/inventories/{inventory_id}/"
        async with httpx.AsyncClient() as client:
            resp = await client.delete(url, headers=self.headers)
            resp.raise_for_status()
            return {"status": "deleted", "id": inventory_id}

    async def sync_inventory(self, inventory_id: int) -> dict:
        """Trigger a sync of an inventory."""
        url = f"{self.base_url}/api/v2/inventories/{inventory_id}/sync/"
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    # NEW INVENTORY METHODS END

# Singleton instance
awx_client = AWXClient()
