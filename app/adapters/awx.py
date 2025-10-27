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
async def list_users(username: str = None):
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
async def list_tools(model_name: str = "granite3.1-dense:2b"):
    """List available tools for LLM function calling."""
    try:
        from app.model_capabilities import get_available_tools

        # Get available tools based on model capabilities
        available_tools = get_available_tools(model_name, 0)

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
