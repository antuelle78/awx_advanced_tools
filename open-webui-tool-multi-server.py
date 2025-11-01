"""
title: 'Ansible AWX Controller - Multi-Server'
author: 'AWX Advanced Tools'
description: 'Connect to specialized AWX MCP servers (multi-server architecture)'
requirements:
  - 'httpx'
  
This tool supports the new multi-server architecture where operations are
split across specialized servers:
  - Core Operations (8001): Job execution and monitoring
  - Inventory Management (8002): Inventory CRUD
  - Templates (8003): Template and host management
  - Users (8004): User management
  - Projects (8005): Project management
  - Organizations (8006): Organization management
  - Schedules (8007): Schedule management
  - Advanced (8008): Credentials, workflows
  - Notifications (8009): Notification templates
  - Infrastructure (8010): Instance groups

You can connect to:
1. Individual servers directly (for focused operations)
2. Gateway (8000) that routes to appropriate servers
"""

import httpx
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import json
import time

class Tools:
    class Valves(BaseModel):
        # Gateway configuration (recommended)
        gateway_url: str = Field(
            default="http://host.docker.internal:8000",
            description="Gateway URL that routes to specialized servers"
        )
        use_gateway: bool = Field(
            default=False,  # Disabled until gateway is implemented
            description="Use gateway for automatic routing (Phase 5)"
        )
        
        # Individual server URLs (for direct connection)
        core_server_url: str = Field(
            default="http://host.docker.internal:8001",
            description="Core Operations server (jobs, templates)"
        )
        inventory_server_url: str = Field(
            default="http://host.docker.internal:8002",
            description="Inventory Management server"
        )
        templates_server_url: str = Field(
            default="http://host.docker.internal:8003",
            description="Templates server (job templates, hosts)"
        )
        users_server_url: str = Field(
            default="http://host.docker.internal:8004",
            description="User Management server"
        )
        projects_server_url: str = Field(
            default="http://host.docker.internal:8005",
            description="Project Management server"
        )
        organizations_server_url: str = Field(
            default="http://host.docker.internal:8006",
            description="Organization Management server"
        )
        schedules_server_url: str = Field(
            default="http://host.docker.internal:8007",
            description="Schedule Management server"
        )
        advanced_server_url: str = Field(
            default="http://host.docker.internal:8008",
            description="Advanced Operations server (credentials, workflows)"
        )
        
        # Authentication (same for all servers)
        mcp_username: str = Field(
            default="openwebui",
            description="Username for MCP server authentication"
        )
        mcp_password: str = Field(
            default="openwebui",
            description="Password for MCP server authentication"
        )
        
        # Model optimization
        model_name: str = Field(
            default="granite3.1-dense:2b",
            description="Current model name for capability optimization"
        )
        enable_model_optimization: bool = Field(
            default=True,
            description="Enable model-aware optimizations"
        )

    def __init__(self):
        self.valves = self.Valves()
        self.client = httpx.Client(
            timeout=30.0,
            auth=(self.valves.mcp_username, self.valves.mcp_password)
        )
        
    def _get_server_for_operation(self, operation: str) -> str:
        """Determine which server to use for a given operation."""
        if self.valves.use_gateway:
            return self.valves.gateway_url
            
        # Map operations to servers
        operation_map = {
            # Core Operations (8001)
            "list_templates": "core",
            "launch_job_template": "core",
            "get_job": "core",
            "list_jobs": "core",
            "test_connection": "core",
            
            # Inventory Management (8002)
            "list_inventories": "inventory",
            "get_inventory": "inventory",
            "create_inventory": "inventory",
            "sync_inventory": "inventory",
            "delete_inventory": "inventory",
            
            # Templates (8003)
            "create_job_template": "templates",
            "list_hosts": "templates",
            "create_host": "templates",
            
            # Users (8004)
            "list_users": "users",
            "get_user": "users",
            "get_user_by_name": "users",
            "create_user": "users",
            "update_user": "users",
            "delete_user": "users",
            
            # Projects (8005)
            "list_projects": "projects",
            "get_project": "projects",
            "create_project": "projects",
            "update_project": "projects",
            "sync_project": "projects",
            "delete_project": "projects",
            
            # Organizations (8006)
            "list_organizations": "organizations",
            "get_organization": "organizations",
            "create_organization": "organizations",
            "update_organization": "organizations",
            "delete_organization": "organizations",
            
            # Schedules (8007)
            "list_schedules": "schedules",
            "get_schedule": "schedules",
            "create_schedule": "schedules",
            "update_schedule": "schedules",
            "delete_schedule": "schedules",
            "toggle_schedule": "schedules",
            
            # Advanced (8008) - Credentials, Workflows, etc.
            "list_credentials": "advanced",
            "create_credential": "advanced",
            "get_credential": "advanced",
            "update_credential": "advanced",
            "delete_credential": "advanced",
            "list_workflow_job_templates": "advanced",
            "create_workflow_job_template": "advanced",
            "launch_workflow_job_template": "advanced",
            "update_workflow_job_template": "advanced",
            "delete_workflow_job_template": "advanced",
        }
        
        server_name = operation_map.get(operation, "core")  # Default to core
        
        # Map server name to URL
        server_urls = {
            "core": self.valves.core_server_url,
            "inventory": self.valves.inventory_server_url,
            "templates": self.valves.templates_server_url,
            "users": self.valves.users_server_url,
            "projects": self.valves.projects_server_url,
            "organizations": self.valves.organizations_server_url,
            "schedules": self.valves.schedules_server_url,
            "advanced": self.valves.advanced_server_url,
        }
        
        return server_urls.get(server_name, self.valves.core_server_url)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {"Content-Type": "application/json"}
    
    def _make_request(self, operation: str, path: str, method: str = "GET",
                     params: Optional[Dict] = None, json_data: Optional[Dict] = None) -> str:
        """Make a request to the appropriate server."""
        server_url = self._get_server_for_operation(operation)
        url = f"{server_url}{path}"
        
        try:
            if method == "GET":
                response = self.client.get(url, headers=self._get_headers(), params=params)
            elif method == "POST":
                response = self.client.post(url, headers=self._get_headers(), json=json_data, params=params)
            elif method == "PATCH":
                response = self.client.patch(url, headers=self._get_headers(), json=json_data)
            elif method == "DELETE":
                response = self.client.delete(url, headers=self._get_headers())
            else:
                return json.dumps({"error": f"Unsupported method: {method}"})
            
            response.raise_for_status()
            
            # Handle empty responses (common for DELETE)
            if not response.content:
                return json.dumps({"status": "success"})
            
            return json.dumps(response.json())
            
        except httpx.HTTPStatusError as e:
            return json.dumps({
                "error": f"HTTP error occurred: {e.response.status_code}",
                "detail": e.response.text,
                "server": server_url,
            })
        except Exception as e:
            return json.dumps({"error": str(e), "server": server_url})
    
    # ===== Core Operations (Port 8001) =====
    
    def list_templates(self, name: Optional[str] = None) -> str:
        """Lists all job templates in AWX, optionally filtered by name."""
        params = {"name": name} if name else {}
        return self._make_request("list_templates", "/job_templates", params=params)
    
    def launch_job_template(self, template_id: int, extra_vars: Optional[Dict[str, Any]] = None) -> str:
        """Launches an AWX job template to start a new job."""
        json_data = {"extra_vars": extra_vars} if extra_vars else {}
        return self._make_request("launch_job_template", f"/job_templates/{template_id}/launch",
                                 method="POST", json_data=json_data)
    
    def get_job(self, job_id: int) -> str:
        """Retrieves current status and details of a specific job."""
        return self._make_request("get_job", f"/jobs/{job_id}")
    
    def list_jobs(self, page: int = 1) -> str:
        """Lists all jobs in AWX with pagination."""
        return self._make_request("list_jobs", "/jobs", params={"page": page})
    
    def test_connection(self) -> str:
        """Tests the connection to the AWX server."""
        return self._make_request("test_connection", "/test")
    
    # ===== Inventory Management (Port 8002) =====
    
    def list_inventories(self, name: Optional[str] = None) -> str:
        """Lists all inventories in AWX, optionally filtered by name."""
        params = {"name": name} if name else {}
        return self._make_request("list_inventories", "/inventories", params=params)
    
    def create_inventory(self, name: str, organization: int, variables: Optional[Dict[str, Any]] = None) -> str:
        """Creates a new inventory in AWX."""
        json_data = {"name": name, "organization": organization}
        if variables:
            json_data["variables"] = variables
        return self._make_request("create_inventory", "/inventories", method="POST", json_data=json_data)
    
    def get_inventory(self, inventory_id: int) -> str:
        """Retrieves details of a specific inventory."""
        return self._make_request("get_inventory", f"/inventories/{inventory_id}")
    
    def sync_inventory(self, inventory_id: int) -> str:
        """Synchronizes an inventory with its source."""
        return self._make_request("sync_inventory", f"/inventories/{inventory_id}/sync", method="POST")
    
    def delete_inventory(self, inventory_id: int) -> str:
        """Deletes an inventory from AWX."""
        return self._make_request("delete_inventory", f"/inventories/{inventory_id}", method="DELETE")
    
    # ===== Job Templates (Port 8003) =====
    
    def create_job_template(self, name: str, inventory: int, project: int, playbook: str,
                          description: Optional[str] = None, extra_vars: Optional[Dict[str, Any]] = None) -> str:
        """Creates a new job template in AWX."""
        params = {"name": name, "inventory": inventory, "project": project, "playbook": playbook}
        json_data = {}
        if description:
            json_data["description"] = description
        if extra_vars:
            json_data["extra_vars"] = extra_vars
        
        return self._make_request("create_job_template", "/job_templates/",
                                 method="POST", params=params, json_data=json_data if json_data else None)
    
    def list_hosts(self, inventory: Optional[int] = None) -> str:
        """Lists all hosts in AWX, optionally filtered by inventory."""
        params = {"inventory": inventory} if inventory else {}
        return self._make_request("list_hosts", "/hosts/", params=params)
    
    def create_host(self, host_data: Dict[str, Any]) -> str:
        """Creates a new host in AWX."""
        return self._make_request("create_host", "/hosts/", method="POST", json_data=host_data)
    
    # ===== User Management (Port 8004) =====
    
    def list_users(self) -> str:
        """Lists all users in AWX."""
        return self._make_request("list_users", "/users")
    
    def get_user(self, user_id: int) -> str:
        """Retrieves details of a specific user."""
        return self._make_request("get_user", f"/users/{user_id}")
    
    def get_user_by_name(self, username: str) -> str:
        """Retrieves user details by username."""
        return self._make_request("get_user_by_name", f"/users/by-name/{username}")
    
    def create_user(self, username: str, password: str, first_name: Optional[str] = None,
                   last_name: Optional[str] = None, email: Optional[str] = None) -> str:
        """Creates a new user in AWX."""
        json_data = {"username": username, "password": password}
        if first_name:
            json_data["first_name"] = first_name
        if last_name:
            json_data["last_name"] = last_name
        if email:
            json_data["email"] = email
        return self._make_request("create_user", "/users", method="POST", json_data=json_data)
    
    def update_user(self, user_id: int, username: Optional[str] = None, first_name: Optional[str] = None,
                   last_name: Optional[str] = None, email: Optional[str] = None) -> str:
        """Updates an existing user in AWX."""
        json_data = {}
        if username:
            json_data["username"] = username
        if first_name:
            json_data["first_name"] = first_name
        if last_name:
            json_data["last_name"] = last_name
        if email:
            json_data["email"] = email
        return self._make_request("update_user", f"/users/{user_id}", method="PATCH", json_data=json_data)
    
    def delete_user(self, user_id: int) -> str:
        """Deletes a user from AWX."""
        return self._make_request("delete_user", f"/users/{user_id}", method="DELETE")
    
    # ===== Project Management (Port 8005) =====
    
    def list_projects(self, name: Optional[str] = None) -> str:
        """Lists all projects in AWX, optionally filtered by name."""
        params = {"name": name} if name else {}
        return self._make_request("list_projects", "/projects", params=params)
    
    def get_project(self, project_id: int) -> str:
        """Retrieves details of a specific project."""
        return self._make_request("get_project", f"/projects/{project_id}")
    
    def create_project(self, name: str, scm_type: str, scm_url: str, description: Optional[str] = None) -> str:
        """Creates a new project in AWX."""
        json_data = {"name": name, "scm_type": scm_type, "scm_url": scm_url}
        if description:
            json_data["description"] = description
        return self._make_request("create_project", "/projects", method="POST", json_data=json_data)
    
    def update_project(self, project_id: int, name: Optional[str] = None, scm_type: Optional[str] = None,
                      scm_url: Optional[str] = None, description: Optional[str] = None) -> str:
        """Updates an existing project in AWX."""
        json_data = {}
        if name:
            json_data["name"] = name
        if scm_type:
            json_data["scm_type"] = scm_type
        if scm_url:
            json_data["scm_url"] = scm_url
        if description:
            json_data["description"] = description
        return self._make_request("update_project", f"/projects/{project_id}", method="PATCH", json_data=json_data)
    
    def sync_project(self, project_id: int) -> str:
        """Synchronizes a project with its source repository."""
        return self._make_request("sync_project", f"/projects/{project_id}/sync", method="POST")
    
    def delete_project(self, project_id: int) -> str:
        """Deletes a project from AWX."""
        return self._make_request("delete_project", f"/projects/{project_id}", method="DELETE")
    
    # ===== Organization Management (Port 8006) =====
    
    def list_organizations(self, name: Optional[str] = None) -> str:
        """Lists all organizations in AWX, optionally filtered by name."""
        params = {"name": name} if name else {}
        return self._make_request("list_organizations", "/organizations", params=params)
    
    def get_organization(self, organization_id: int) -> str:
        """Retrieves details of a specific organization."""
        return self._make_request("get_organization", f"/organizations/{organization_id}")
    
    def create_organization(self, name: str, description: Optional[str] = None) -> str:
        """Creates a new organization in AWX."""
        json_data = {"name": name}
        if description:
            json_data["description"] = description
        return self._make_request("create_organization", "/organizations", method="POST", json_data=json_data)
    
    def update_organization(self, organization_id: int, name: Optional[str] = None,
                           description: Optional[str] = None) -> str:
        """Updates an existing organization in AWX."""
        json_data = {}
        if name:
            json_data["name"] = name
        if description:
            json_data["description"] = description
        return self._make_request("update_organization", f"/organizations/{organization_id}",
                                 method="PATCH", json_data=json_data)
    
    def delete_organization(self, organization_id: int) -> str:
        """Deletes an organization from AWX."""
        return self._make_request("delete_organization", f"/organizations/{organization_id}", method="DELETE")
    
    # ===== Schedule Management (Port 8007) =====
    
    def list_schedules(self, template_id: int) -> str:
        """Lists all schedules for a specific job template."""
        return self._make_request("list_schedules", f"/job_templates/{template_id}/schedules")
    
    def get_schedule(self, schedule_id: int) -> str:
        """Retrieves details of a specific schedule."""
        return self._make_request("get_schedule", f"/schedules/{schedule_id}")
    
    def create_schedule(self, template_id: int, name: str, rrule: str) -> str:
        """Creates a new schedule for a job template."""
        json_data = {"name": name, "rrule": rrule}
        return self._make_request("create_schedule", f"/job_templates/{template_id}/schedules",
                                 method="POST", json_data=json_data)
    
    def update_schedule(self, schedule_id: int, name: Optional[str] = None, rrule: Optional[str] = None,
                       enabled: Optional[bool] = None) -> str:
        """Updates an existing schedule."""
        json_data = {}
        if name:
            json_data["name"] = name
        if rrule:
            json_data["rrule"] = rrule
        if enabled is not None:
            json_data["enabled"] = enabled
        return self._make_request("update_schedule", f"/schedules/{schedule_id}",
                                 method="PATCH", json_data=json_data)
    
    def delete_schedule(self, schedule_id: int) -> str:
        """Deletes a schedule from AWX."""
        return self._make_request("delete_schedule", f"/schedules/{schedule_id}", method="DELETE")
    
    def toggle_schedule(self, schedule_id: int, enabled: bool) -> str:
        """Toggles a schedule enabled/disabled."""
        json_data = {"enabled": enabled}
        return self._make_request("toggle_schedule", f"/schedules/{schedule_id}",
                                 method="PATCH", json_data=json_data)
