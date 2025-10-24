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

# Singleton instance
awx_client = AWXClient()
