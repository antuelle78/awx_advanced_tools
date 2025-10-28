from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from app.adapters.awx_service import awx_client
import httpx

router = APIRouter(prefix="/awx", tags=["AWX"])


class InventoryCreate(BaseModel):
    name: str
    organization: int
    variables: Optional[Dict] = None


class UserCreate(BaseModel):
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None


class ProjectCreate(BaseModel):
    name: str
    scm_type: str
    scm_url: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    scm_type: Optional[str] = None
    scm_url: Optional[str] = None
    description: Optional[str] = None


class OrganizationCreate(BaseModel):
    name: str
    description: Optional[str] = None


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


@router.post("/job_templates/{template_id}/launch")
async def launch_job_template(template_id: int, extra_vars: dict | None = None):
    return await awx_client.launch_job_template(template_id, extra_vars)

@router.post("/job_templates/")
async def create_job_template(
    name: str,
    inventory: int,
    project: int,
    playbook: str,
    description: str | None = None,
    extra_vars: dict | None = None,
):
    return await awx_client.create_job_template(name, inventory, project, playbook, description, extra_vars)

@router.get("/hosts/")
async def list_hosts(inventory: Optional[int] = None):
    try:
        return await awx_client.list_hosts(inventory)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))

@router.post("/hosts/")
async def create_host(host_data: dict):
    try:
        return await awx_client.create_host(host_data)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# User endpoints
@router.get("/users")
async def list_users(username: Optional[str] = None):
    try:
        return await awx_client.list_users(username)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/test")
async def test():
    return {"test": "ok"}


@router.get("/users/{user_id}")
async def get_user(user_id: int):
    try:
        return await awx_client.get_user(user_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/users/by-name/{username}")
async def get_user_by_name(username: str):
    try:
        return await awx_client.get_user_by_name(username)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/users")
async def create_user(user: UserCreate):
    try:
        return await awx_client.create_user(
            user.username, user.password, user.first_name, user.last_name, user.email
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.patch("/users/{user_id}")
async def update_user(user_id: int, user: UserUpdate):
    try:
        return await awx_client.update_user(
            user_id, user.username, user.first_name, user.last_name, user.email
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    try:
        return await awx_client.delete_user(user_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/inventories")
async def list_inventories(name: Optional[str] = None):
    try:
        return await awx_client.list_inventories(name)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/inventories")
async def create_inventory(inventory: InventoryCreate, dry_run: bool = False):
    if dry_run:
        return {
            "status": "dry_run",
            "action": "create_inventory",
            "name": inventory.name,
            "organization": inventory.organization,
        }
    try:
        return await awx_client.create_inventory(
            inventory.name, inventory.variables, inventory.organization
        )
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/inventories/{inventory_id}")
async def get_inventory(inventory_id: int):
    try:
        return await awx_client.get_inventory(inventory_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.delete("/inventories/{inventory_id}")
async def delete_inventory(inventory_id: int, dry_run: bool = False):
    if dry_run:
        return {"status": "dry_run", "action": "delete_inventory", "id": inventory_id}
    try:
        await awx_client.delete_inventory(inventory_id)
        return {"status": "deleted", "id": inventory_id}
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/inventories/{inventory_id}/sync")
async def sync_inventory(inventory_id: int):
    try:
        return await awx_client.sync_inventory(inventory_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/job_templates/{template_id}/schedules")
async def list_schedules(template_id: int):
    try:
        return await awx_client.list_schedules(template_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.patch("/schedules/{schedule_id}")
async def toggle_schedule(schedule_id: int, enabled: bool):
    try:
        return await awx_client.toggle_schedule(schedule_id, enabled)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


class ScheduleCreate(BaseModel):
    name: str
    rrule: str
    job_template_id: int


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: int):
    try:
        return await awx_client.delete_schedule(schedule_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/templates")
async def list_templates(name: Optional[str] = None):
    try:
        return await awx_client.list_templates(name)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/jobs")
async def list_jobs(page: int = 1):
    try:
        return await awx_client.list_jobs(page)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/jobs/{job_id}")
async def get_job(job_id: int):
    try:
        return await awx_client.get_job(job_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/schedules/{schedule_id}")
async def get_schedule(schedule_id: int):
    try:
        return await awx_client.get_schedule(schedule_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/job_templates/{template_id}/schedules")
async def create_schedule(template_id: int, schedule: ScheduleCreate):
    try:
        return await awx_client.create_schedule(
            name=schedule.name, rrule=schedule.rrule, job_template_id=template_id
        )
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


# Project endpoints
@router.get("/projects")
async def list_projects(name: Optional[str] = None):
    try:
        return await awx_client.list_projects(name)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/projects/{project_id}")
async def get_project(project_id: int):
    try:
        return await awx_client.get_project(project_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/projects")
async def create_project(project: ProjectCreate):
    try:
        return await awx_client.create_project(
            project.name, project.scm_type, project.scm_url, project.description
        )
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.patch("/projects/{project_id}")
async def update_project(project_id: int, project: ProjectUpdate):
    try:
        return await awx_client.update_project(
            project_id,
            project.name,
            project.scm_type,
            project.scm_url,
            project.description,
        )
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.delete("/projects/{project_id}")
async def delete_project(project_id: int, dry_run: bool = False):
    if dry_run:
        return {"status": "dry_run", "action": "delete_project", "id": project_id}
    try:
        return await awx_client.delete_project(project_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/projects/{project_id}/sync")
async def sync_project(project_id: int):
    try:
        return await awx_client.sync_project(project_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


# Organization endpoints
@router.get("/organizations")
async def list_organizations(name: Optional[str] = None):
    try:
        return await awx_client.list_organizations(name)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/organizations/{organization_id}")
async def get_organization(organization_id: int):
    try:
        return await awx_client.get_organization(organization_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/organizations")
async def create_organization(organization: OrganizationCreate):
    try:
        return await awx_client.create_organization(
            organization.name, organization.description
        )
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.patch("/organizations/{organization_id}")
async def update_organization(organization_id: int, organization: OrganizationUpdate):
    try:
        return await awx_client.update_organization(
            organization_id, organization.name, organization.description
        )
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.delete("/organizations/{organization_id}")
async def delete_organization(organization_id: int):
    try:
        return await awx_client.delete_organization(organization_id)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


# Tools endpoint for LLM discovery
@router.get("/tools")
async def list_tools(model_name: str = "granite3.1-dense:2b", conversation_id: Optional[str] = None):
    """List available tools for LLM function calling."""
    try:
        from app.model_capabilities import get_available_tools
        from app.context_manager import context_manager

        # Get conversation length for progressive tool exposure
        conversation_length = 0
        if conversation_id:
            context = context_manager.get_context(conversation_id, model_name)
            conversation_length = len(context.tool_calls)

        # Get available tools based on model capabilities and conversation context
        available_tools = get_available_tools(model_name, conversation_length)

        # Define tool schemas
        tool_definitions = {
            "list_templates": {
                "type": "function",
                "function": {
                    "name": "list_templates",
                    "description": "Lists all job templates in AWX, optionally filtered by name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Optional name to filter job templates"
                            }
                        }
                    }
                }
            },
            "launch_job_template": {
                "type": "function",
                "function": {
                    "name": "launch_job_template",
                    "description": "Launches an AWX job template to start a new job",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "template_id": {
                                "type": "integer",
                                "description": "The ID of job template to launch"
                            },
                            "extra_vars": {
                                "type": "object",
                                "description": "Optional extra variables to pass to the job"
                            }
                        },
                        "required": ["template_id"]
                    }
                }
            },
            "create_job_template": {
                "type": "function",
                "function": {
                    "name": "create_job_template",
                    "description": "Creates a new job template in AWX. Requires numeric IDs for inventory and project (use list_inventories and list_projects to resolve names to IDs first).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the job template"
                            },
                            "inventory": {
                                "type": "integer",
                                "description": "Numeric ID of the inventory (resolve from list_inventories)"
                            },
                            "project": {
                                "type": "integer",
                                "description": "Numeric ID of the project (resolve from list_projects)"
                            },
                            "playbook": {
                                "type": "string",
                                "description": "Path to the playbook file in the project"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional description for the job template"
                            },
                            "extra_vars": {
                                "type": "object",
                                "description": "Optional extra variables for the job template"
                            }
                        },
                        "required": ["name", "inventory", "project", "playbook"]
                    }
                }
            },
            "get_job": {
                "type": "function",
                "function": {
                    "name": "get_job",
                    "description": "Retrieves current status and details of a specific job",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "job_id": {
                                "type": "integer",
                                "description": "The ID of job to retrieve"
                            }
                        },
                        "required": ["job_id"]
                    }
                }
            },
            "list_jobs": {
                "type": "function",
                "function": {
                    "name": "list_jobs",
                    "description": "Lists all jobs in AWX with pagination",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "page": {
                                "type": "integer",
                                "description": "The page number for pagination",
                                "default": 1
                            }
                        }
                    }
                }
            },
            "list_inventories": {
                "type": "function",
                "function": {
                    "name": "list_inventories",
                    "description": "Lists all inventories in AWX, optionally filtered by name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Optional name to filter inventories"
                            }
                        }
                    }
                }
            },
            "create_inventory": {
                "type": "function",
                "function": {
                    "name": "create_inventory",
                    "description": "Creates a new inventory in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the inventory"
                            },
                            "organization": {
                                "type": "integer",
                                "description": "ID of the organization"
                            },
                            "variables": {
                                "type": "object",
                                "description": "Optional variables for the inventory"
                            }
                        },
                        "required": ["name", "organization"]
                    }
                }
            },
            "get_inventory": {
                "type": "function",
                "function": {
                    "name": "get_inventory",
                    "description": "Retrieves details of a specific inventory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "inventory_id": {
                                "type": "integer",
                                "description": "The ID of inventory to retrieve"
                            }
                        },
                        "required": ["inventory_id"]
                    }
                }
            },
            "sync_inventory": {
                "type": "function",
                "function": {
                    "name": "sync_inventory",
                    "description": "Synchronizes an inventory with its source",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "inventory_id": {
                                "type": "integer",
                                "description": "The ID of inventory to sync"
                            }
                        },
                        "required": ["inventory_id"]
                    }
                }
            },
            "list_users": {
                "type": "function",
                "function": {
                    "name": "list_users",
                    "description": "Lists all users in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            "create_user": {
                "type": "function",
                "function": {
                    "name": "create_user",
                    "description": "Creates a new user in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "username": {
                                "type": "string",
                                "description": "Username for the new user"
                            },
                            "password": {
                                "type": "string",
                                "description": "Password for the new user"
                            },
                            "first_name": {
                                "type": "string",
                                "description": "Optional first name"
                            },
                            "last_name": {
                                "type": "string",
                                "description": "Optional last name"
                            },
                            "email": {
                                "type": "string",
                                "description": "Optional email address"
                            }
                        },
                        "required": ["username", "password"]
                    }
                }
            },
            "get_user": {
                "type": "function",
                "function": {
                    "name": "get_user",
                    "description": "Retrieves details of a specific user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "The ID of user to retrieve"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            },
            "list_projects": {
                "type": "function",
                "function": {
                    "name": "list_projects",
                    "description": "Lists all projects in AWX, optionally filtered by name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Optional name to filter projects"
                            }
                        }
                    }
                }
            },
            "create_project": {
                "type": "function",
                "function": {
                    "name": "create_project",
                    "description": "Creates a new project in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the project"
                            },
                            "scm_type": {
                                "type": "string",
                                "description": "Type of source control (git, svn, etc.)"
                            },
                            "scm_url": {
                                "type": "string",
                                "description": "URL of the source repository"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional description"
                            }
                        },
                        "required": ["name", "scm_type", "scm_url"]
                    }
                }
            },
            "sync_project": {
                "type": "function",
                "function": {
                    "name": "sync_project",
                    "description": "Synchronizes a project with its source repository",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "integer",
                                "description": "The ID of project to sync"
                            }
                        },
                        "required": ["project_id"]
                    }
                }
            },
            "list_organizations": {
                "type": "function",
                "function": {
                    "name": "list_organizations",
                    "description": "Lists all organizations in AWX, optionally filtered by name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Optional name to filter organizations"
                            }
                        }
                    }
                }
            },
            "create_organization": {
                "type": "function",
                "function": {
                    "name": "create_organization",
                    "description": "Creates a new organization in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the organization"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional description"
                            }
                        },
                        "required": ["name"]
                    }
                }
            },
            "list_hosts": {
                "type": "function",
                "function": {
                    "name": "list_hosts",
                    "description": "Lists all hosts in AWX, optionally filtered by inventory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "inventory": {
                                "type": "integer",
                                "description": "Optional inventory ID to filter hosts"
                            }
                        }
                    }
                }
            },
            "create_host": {
                "type": "function",
                "function": {
                    "name": "create_host",
                    "description": "Creates a new host in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "host_data": {
                                "type": "object",
                                "description": "Host details including name, inventory, etc."
                            }
                        },
                        "required": ["host_data"]
                    }
                }
            },
            "list_schedules": {
                "type": "function",
                "function": {
                    "name": "list_schedules",
                    "description": "Lists all schedules for a specific job template",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "template_id": {
                                "type": "integer",
                                "description": "The ID of job template to list schedules for"
                            }
                        },
                        "required": ["template_id"]
                    }
                }
            },
            "create_schedule": {
                "type": "function",
                "function": {
                    "name": "create_schedule",
                    "description": "Creates a new schedule for a job template",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "template_id": {
                                "type": "integer",
                                "description": "The ID of job template to create schedule for"
                            },
                            "name": {
                                "type": "string",
                                "description": "Name of the schedule"
                            },
                            "rrule": {
                                "type": "string",
                                "description": "RRULE string defining the schedule recurrence"
                            }
                        },
                        "required": ["template_id", "name", "rrule"]
                    }
                }
            },
            "get_schedule": {
                "type": "function",
                "function": {
                    "name": "get_schedule",
                    "description": "Retrieves details of a specific schedule",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "schedule_id": {
                                "type": "integer",
                                "description": "The ID of schedule to retrieve"
                            }
                        },
                        "required": ["schedule_id"]
                    }
                }
            },
            "toggle_schedule": {
                "type": "function",
                "function": {
                    "name": "toggle_schedule",
                    "description": "Enables or disables a schedule",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "schedule_id": {
                                "type": "integer",
                                "description": "The ID of schedule to toggle"
                            },
                            "enabled": {
                                "type": "boolean",
                                "description": "Whether to enable or disable the schedule"
                            }
                        },
                        "required": ["schedule_id", "enabled"]
                    }
                }
            },
            "list_activity_stream": {
                "type": "function",
                "function": {
                    "name": "list_activity_stream",
                    "description": "Lists activity stream events in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "page": {
                                "type": "integer",
                                "description": "The page number",
                                "default": 1
                            },
                            "page_size": {
                                "type": "integer",
                                "description": "The number of items per page",
                                "default": 20
                            }
                        }
                    }
                }
            },
            "health_check": {
                "type": "function",
                "function": {
                    "name": "health_check",
                    "description": "Performs a health check on the AWX connection",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            "test_connection": {
                "type": "function",
                "function": {
                    "name": "test_connection",
                    "description": "Tests the connection to the AWX server",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            "get_user_by_name": {
                "type": "function",
                "function": {
                    "name": "get_user_by_name",
                    "description": "Retrieves user details by username",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "username": {
                                "type": "string",
                                "description": "The username to search for"
                            }
                        },
                        "required": ["username"]
                    }
                }
            },
            "update_user": {
                "type": "function",
                "function": {
                    "name": "update_user",
                    "description": "Updates an existing user in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "The ID of user to update"
                            },
                            "username": {
                                "type": "string",
                                "description": "Optional new username"
                            },
                            "first_name": {
                                "type": "string",
                                "description": "Optional new first name"
                            },
                            "last_name": {
                                "type": "string",
                                "description": "Optional new last name"
                            },
                            "email": {
                                "type": "string",
                                "description": "Optional new email"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            },
            "delete_user": {
                "type": "function",
                "function": {
                    "name": "delete_user",
                    "description": "Deletes a user from AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "The ID of user to delete"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            },
            "delete_inventory": {
                "type": "function",
                "function": {
                    "name": "delete_inventory",
                    "description": "Deletes an inventory from AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "inventory_id": {
                                "type": "integer",
                                "description": "The ID of inventory to delete"
                            },
                            "confirm": {
                                "type": "boolean",
                                "description": "Confirmation flag for deletion",
                                "default": False
                            },
                            "dry_run": {
                                "type": "boolean",
                                "description": "Perform dry run without actual deletion",
                                "default": False
                            }
                        },
                        "required": ["inventory_id"]
                    }
                }
            },
            "get_project": {
                "type": "function",
                "function": {
                    "name": "get_project",
                    "description": "Retrieves details of a specific project",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "integer",
                                "description": "The ID of project to retrieve"
                            }
                        },
                        "required": ["project_id"]
                    }
                }
            },
            "update_project": {
                "type": "function",
                "function": {
                    "name": "update_project",
                    "description": "Updates an existing project in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "integer",
                                "description": "The ID of project to update"
                            },
                            "name": {
                                "type": "string",
                                "description": "Optional new name"
                            },
                            "scm_type": {
                                "type": "string",
                                "description": "Optional new SCM type"
                            },
                            "scm_url": {
                                "type": "string",
                                "description": "Optional new SCM URL"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional new description"
                            }
                        },
                        "required": ["project_id"]
                    }
                }
            },
            "delete_project": {
                "type": "function",
                "function": {
                    "name": "delete_project",
                    "description": "Deletes a project from AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "integer",
                                "description": "The ID of project to delete"
                            },
                            "confirm": {
                                "type": "boolean",
                                "description": "Confirmation flag for deletion",
                                "default": False
                            },
                            "dry_run": {
                                "type": "boolean",
                                "description": "Perform dry run without actual deletion",
                                "default": False
                            }
                        },
                        "required": ["project_id"]
                    }
                }
            },
            "get_organization": {
                "type": "function",
                "function": {
                    "name": "get_organization",
                    "description": "Retrieves details of a specific organization",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "organization_id": {
                                "type": "integer",
                                "description": "The ID of organization to retrieve"
                            }
                        },
                        "required": ["organization_id"]
                    }
                }
            },
            "update_organization": {
                "type": "function",
                "function": {
                    "name": "update_organization",
                    "description": "Updates an existing organization in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "organization_id": {
                                "type": "integer",
                                "description": "The ID of organization to update"
                            },
                            "name": {
                                "type": "string",
                                "description": "Optional new name"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional new description"
                            }
                        },
                        "required": ["organization_id"]
                    }
                }
            },
            "delete_organization": {
                "type": "function",
                "function": {
                    "name": "delete_organization",
                    "description": "Deletes an organization from AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "organization_id": {
                                "type": "integer",
                                "description": "The ID of organization to delete"
                            }
                        },
                        "required": ["organization_id"]
                    }
                }
            },
            "update_schedule": {
                "type": "function",
                "function": {
                    "name": "update_schedule",
                    "description": "Updates an existing schedule",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "schedule_id": {
                                "type": "integer",
                                "description": "The ID of schedule to update"
                            },
                            "name": {
                                "type": "string",
                                "description": "Optional new name"
                            },
                            "rrule": {
                                "type": "string",
                                "description": "Optional new RRULE string"
                            },
                            "enabled": {
                                "type": "boolean",
                                "description": "Optional enabled/disabled status"
                            }
                        },
                        "required": ["schedule_id"]
                    }
                }
            },
            "delete_schedule": {
                "type": "function",
                "function": {
                    "name": "delete_schedule",
                    "description": "Deletes a schedule from AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "schedule_id": {
                                "type": "integer",
                                "description": "The ID of schedule to delete"
                            }
                        },
                        "required": ["schedule_id"]
                    }
                }
            },
            "list_credentials": {
                "type": "function",
                "function": {
                    "name": "list_credentials",
                    "description": "Lists credentials in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            "get_credential": {
                "type": "function",
                "function": {
                    "name": "get_credential",
                    "description": "Retrieves details of a specific credential",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "credential_id": {
                                "type": "integer",
                                "description": "The ID of credential to retrieve"
                            }
                        },
                        "required": ["credential_id"]
                    }
                }
            },
            "create_credential": {
                "type": "function",
                "function": {
                    "name": "create_credential",
                    "description": "Creates a new credential in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the credential"
                            },
                            "credential_type": {
                                "type": "integer",
                                "description": "Type ID of the credential"
                            },
                            "inputs": {
                                "type": "object",
                                "description": "Credential inputs"
                            }
                        },
                        "required": ["name", "credential_type", "inputs"]
                    }
                }
            },
            "update_credential": {
                "type": "function",
                "function": {
                    "name": "update_credential",
                    "description": "Updates an existing credential in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "credential_id": {
                                "type": "integer",
                                "description": "The ID of credential to update"
                            },
                            "name": {
                                "type": "string",
                                "description": "Optional new name"
                            },
                            "inputs": {
                                "type": "object",
                                "description": "Optional new inputs"
                            }
                        },
                        "required": ["credential_id"]
                    }
                }
            },
            "delete_credential": {
                "type": "function",
                "function": {
                    "name": "delete_credential",
                    "description": "Deletes a credential from AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "credential_id": {
                                "type": "integer",
                                "description": "The ID of credential to delete"
                            }
                        },
                        "required": ["credential_id"]
                    }
                }
            },
            "list_workflow_job_templates": {
                "type": "function",
                "function": {
                    "name": "list_workflow_job_templates",
                    "description": "Lists workflow job templates in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            "create_workflow_job_template": {
                "type": "function",
                "function": {
                    "name": "create_workflow_job_template",
                    "description": "Creates a new workflow job template in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the workflow job template"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional description"
                            }
                        },
                        "required": ["name"]
                    }
                }
            },
            "launch_workflow_job_template": {
                "type": "function",
                "function": {
                    "name": "launch_workflow_job_template",
                    "description": "Launches a workflow job template in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "workflow_job_template_id": {
                                "type": "integer",
                                "description": "The ID of workflow job template to launch"
                            },
                            "extra_vars": {
                                "type": "object",
                                "description": "Optional extra variables"
                            }
                        },
                        "required": ["workflow_job_template_id"]
                    }
                }
            },
            "update_workflow_job_template": {
                "type": "function",
                "function": {
                    "name": "update_workflow_job_template",
                    "description": "Updates a workflow job template in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "workflow_job_template_id": {
                                "type": "integer",
                                "description": "The ID of workflow job template to update"
                            },
                            "name": {
                                "type": "string",
                                "description": "Optional new name"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional new description"
                            }
                        },
                        "required": ["workflow_job_template_id"]
                    }
                }
            },
            "delete_workflow_job_template": {
                "type": "function",
                "function": {
                    "name": "delete_workflow_job_template",
                    "description": "Deletes a workflow job template in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "workflow_job_template_id": {
                                "type": "integer",
                                "description": "The ID of workflow job template to delete"
                            }
                        },
                        "required": ["workflow_job_template_id"]
                    }
                }
            },
            "list_notifications": {
                "type": "function",
                "function": {
                    "name": "list_notifications",
                    "description": "Lists notification templates in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            "get_notification": {
                "type": "function",
                "function": {
                    "name": "get_notification",
                    "description": "Retrieves details of a specific notification template",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "notification_id": {
                                "type": "integer",
                                "description": "The ID of notification template to retrieve"
                            }
                        },
                        "required": ["notification_id"]
                    }
                }
            },
            "create_notification": {
                "type": "function",
                "function": {
                    "name": "create_notification",
                    "description": "Creates a new notification template in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the notification template"
                            },
                            "notification_type": {
                                "type": "string",
                                "description": "Type of notification"
                            },
                            "notification_configuration": {
                                "type": "object",
                                "description": "Notification configuration"
                            }
                        },
                        "required": ["name", "notification_type", "notification_configuration"]
                    }
                }
            },
            "update_notification": {
                "type": "function",
                "function": {
                    "name": "update_notification",
                    "description": "Updates a notification template in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "notification_id": {
                                "type": "integer",
                                "description": "The ID of notification template to update"
                            },
                            "name": {
                                "type": "string",
                                "description": "Optional new name"
                            },
                            "notification_configuration": {
                                "type": "object",
                                "description": "Optional new configuration"
                            }
                        },
                        "required": ["notification_id"]
                    }
                }
            },
            "delete_notification": {
                "type": "function",
                "function": {
                    "name": "delete_notification",
                    "description": "Deletes a notification template from AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "notification_id": {
                                "type": "integer",
                                "description": "The ID of notification template to delete"
                            }
                        },
                        "required": ["notification_id"]
                    }
                }
            },
            "list_instance_groups": {
                "type": "function",
                "function": {
                    "name": "list_instance_groups",
                    "description": "Lists instance groups in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            "get_instance_group": {
                "type": "function",
                "function": {
                    "name": "get_instance_group",
                    "description": "Retrieves details of a specific instance group",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "instance_group_id": {
                                "type": "integer",
                                "description": "The ID of instance group to retrieve"
                            }
                        },
                        "required": ["instance_group_id"]
                    }
                }
            },
            "create_instance_group": {
                "type": "function",
                "function": {
                    "name": "create_instance_group",
                    "description": "Creates a new instance group in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the instance group"
                            },
                            "policy_instance_percentage": {
                                "type": "integer",
                                "description": "Optional policy instance percentage"
                            },
                            "policy_instance_minimum": {
                                "type": "integer",
                                "description": "Optional policy instance minimum"
                            }
                        },
                        "required": ["name"]
                    }
                }
            },
            "update_instance_group": {
                "type": "function",
                "function": {
                    "name": "update_instance_group",
                    "description": "Updates an instance group in AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "instance_group_id": {
                                "type": "integer",
                                "description": "The ID of instance group to update"
                            },
                            "name": {
                                "type": "string",
                                "description": "Optional new name"
                            },
                            "policy_instance_percentage": {
                                "type": "integer",
                                "description": "Optional new policy percentage"
                            },
                            "policy_instance_minimum": {
                                "type": "integer",
                                "description": "Optional new policy minimum"
                            }
                        },
                        "required": ["instance_group_id"]
                    }
                }
            },
            "delete_instance_group": {
                "type": "function",
                "function": {
                    "name": "delete_instance_group",
                    "description": "Deletes an instance group from AWX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "instance_group_id": {
                                "type": "integer",
                                "description": "The ID of instance group to delete"
                            }
                        },
                        "required": ["instance_group_id"]
                    }
                }
            }
        }

        # Filter tools based on model capabilities
        available_tool_definitions = []
        for tool_name in available_tools:
            if tool_name in tool_definitions:
                available_tool_definitions.append(tool_definitions[tool_name])

        return {"tools": available_tool_definitions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tools: {str(e)}")


# Activity Stream endpoints
@router.get("/activity_stream")
async def list_activity_stream(page: int = 1, page_size: int = 20):
    try:
        return await awx_client.list_activity_stream(page, page_size)
    except httpx.HTTPStatusError as exc:  # pragma: no cover
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
