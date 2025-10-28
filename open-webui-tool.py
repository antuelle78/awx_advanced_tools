"""
title: 'Ansible AWX Controller'
author: 'Michael Nelson'
description: 'A tool to interact with Ansible AWX through the MCP Server.'
requirements:
  - 'httpx'
"""

import httpx
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import json
import time
import uuid


class PromptOptimizer:
    """Optimizes prompts for better LLM tool usage success rate."""

    def __init__(self):
        self.detailed_prompts = self._load_detailed_prompts()
        self.simple_prompts = self._load_simple_prompts()
        self.confidence_threshold = 0.8
        self.log_file = "tool_usage.log"

    def _load_detailed_prompts(self) -> Dict[str, str]:
        """Load detailed prompts for larger models."""
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
            "create_job_template": "Think step by step: 1. Resolve inventory and project IDs using list_inventories and list_projects. 2. Call create_job_template with IDs. 3. Verify creation. Example: name='web-deploy', inventory=5, project=10, playbook='deploy.yml'.",
            "get_project": "Think step by step: 1. Get project_id from list_projects. 2. Call get_project. 3. Use details. Example: project_id=10.",
            "update_project": "Think step by step: 1. Get project_id. 2. Call update_project with new values. 3. Confirm changes. Example: project_id=10, name='Updated Project'.",
            "delete_project": "Think step by step: 1. Confirm deletion. 2. Use dry_run if testing. 3. Call delete_project. Example: project_id=10, confirm=true.",
            "get_organization": "Think step by step: 1. Get organization_id from list_organizations. 2. Call get_organization. 3. Use details. Example: organization_id=2.",
            "update_organization": "Think step by step: 1. Get organization_id. 2. Call update_organization. 3. Confirm changes. Example: organization_id=2, name='Updated Org'.",
            "delete_organization": "Think step by step: 1. Confirm deletion. 2. Call delete_organization. Example: organization_id=2.",
            "list_schedules": "Think step by step: 1. Get template_id from list_templates. 2. Call list_schedules. 3. Review schedules. Example: template_id=123.",
            "create_schedule": "Think step by step: 1. Get template_id. 2. Define RRULE for recurrence. 3. Call create_schedule. Example: template_id=123, name='Daily Backup', rrule='FREQ=DAILY'.",
            "get_schedule": "Think step by step: 1. Get schedule_id from list_schedules. 2. Call get_schedule. 3. Use details. Example: schedule_id=456.",
            "update_schedule": "Think step by step: 1. Get schedule_id. 2. Call update_schedule with new values. 3. Confirm changes. Example: schedule_id=456, enabled=false.",
            "delete_schedule": "Think step by step: 1. Confirm deletion. 2. Call delete_schedule. Example: schedule_id=456.",
            "toggle_schedule": "Think step by step: 1. Get schedule_id. 2. Call toggle_schedule with enabled status. Example: schedule_id=456, enabled=true.",
            "list_activity_stream": "Think step by step: 1. Specify page and page_size. 2. Call list_activity_stream. 3. Review recent activities. Example: page=1, page_size=20.",
            "health_check": "Think step by step: 1. Call health_check. 2. Verify server status. Example: health_check().",
            "test_connection": "Think step by step: 1. Call test_connection. 2. Check connectivity. Example: test_connection().",
            "get_user_by_name": "Think step by step: 1. Use username. 2. Call get_user_by_name. 3. Get user details. Example: username='admin'.",
            "list_projects": "Think step by step: 1. List projects to find IDs. 2. Use name to filter. 3. Use for other operations. Example: list_projects(name='web').",
            "create_project": "Think step by step: 1. Choose SCM type and URL. 2. Call create_project. 3. Verify creation. Example: name='web-app', scm_type='git', scm_url='https://github.com/user/repo'.",
            "sync_project": "Think step by step: 1. Get project_id. 2. Call sync_project. 3. Monitor sync job. Example: project_id=10.",
            "list_organizations": "Think step by step: 1. List organizations. 2. Use name to filter. 3. Use for other operations. Example: list_organizations(name='DevOps').",
            "create_organization": "Think step by step: 1. Choose unique name. 2. Call create_organization. 3. Verify creation. Example: name='New Org', description='Description'.",
            "create_host": "Think step by step: 1. Prepare host data with name and inventory. 2. Call create_host. 3. Verify creation. Example: host_data={'name': 'web01', 'inventory': 5}.",
            "list_credentials": "Think step by step: 1. List credentials. 2. Use for other operations. Example: list_credentials().",
            "create_credential": "Think step by step: 1. Get credential_type ID. 2. Prepare inputs. 3. Call create_credential. Example: name='aws-key', credential_type=1, inputs={'username': 'user', 'password': 'pass'}.",
            "get_credential": "Think step by step: 1. Get credential_id from list_credentials. 2. Call get_credential. 3. Use details. Example: credential_id=7.",
            "update_credential": "Think step by step: 1. Get credential_id. 2. Call update_credential. 3. Confirm changes. Example: credential_id=7, name='Updated Key'.",
            "delete_credential": "Think step by step: 1. Confirm deletion. 2. Call delete_credential. Example: credential_id=7.",
            "list_workflow_job_templates": "Think step by step: 1. List workflow templates. 2. Use for launching workflows. Example: list_workflow_job_templates().",
            "create_workflow_job_template": "Think step by step: 1. Choose name. 2. Call create_workflow_job_template. 3. Verify creation. Example: name='CI Pipeline', description='Automated CI'.",
            "launch_workflow_job_template": "Think step by step: 1. Get workflow_job_template_id. 2. Prepare extra_vars. 3. Call launch_workflow_job_template. Example: workflow_job_template_id=8, extra_vars={'branch': 'main'}.",
            "update_workflow_job_template": "Think step by step: 1. Get workflow_job_template_id. 2. Call update_workflow_job_template. 3. Confirm changes. Example: workflow_job_template_id=8, name='Updated Pipeline'.",
            "delete_workflow_job_template": "Think step by step: 1. Confirm deletion. 2. Call delete_workflow_job_template. Example: workflow_job_template_id=8.",
            "list_notifications": "Think step by step: 1. List notification templates. 2. Use for other operations. Example: list_notifications().",
            "create_notification": "Think step by step: 1. Choose notification_type and config. 2. Call create_notification. 3. Verify creation. Example: name='Email Alert', notification_type='email', notification_configuration={'recipients': ['admin@example.com']}.",
            "get_notification": "Think step by step: 1. Get notification_id from list_notifications. 2. Call get_notification. 3. Use details. Example: notification_id=9.",
            "update_notification": "Think step by step: 1. Get notification_id. 2. Call update_notification. 3. Confirm changes. Example: notification_id=9, name='Updated Alert'.",
            "delete_notification": "Think step by step: 1. Confirm deletion. 2. Call delete_notification. Example: notification_id=9.",
            "list_instance_groups": "Think step by step: 1. List instance groups. 2. Use for scaling. Example: list_instance_groups().",
            "create_instance_group": "Think step by step: 1. Choose name and policies. 2. Call create_instance_group. 3. Verify creation. Example: name='High Priority', policy_instance_percentage=50.",
            "get_instance_group": "Think step by step: 1. Get instance_group_id from list_instance_groups. 2. Call get_instance_group. 3. Use details. Example: instance_group_id=10.",
            "update_instance_group": "Think step by step: 1. Get instance_group_id. 2. Call update_instance_group. 3. Confirm changes. Example: instance_group_id=10, name='Updated Group'.",
            "delete_instance_group": "Think step by step: 1. Confirm deletion. 2. Call delete_instance_group. Example: instance_group_id=10.",
        }

    def _load_simple_prompts(self) -> Dict[str, str]:
        """Load simplified prompts for smaller models."""
        return {
            "list_templates": "List job templates. Use name to filter. Example: list_templates(name='web')",
            "launch_job_template": "Launch job template with ID and optional variables. Example: launch_job_template(template_id=123, extra_vars={'env': 'prod'})",
            "list_jobs": "List jobs with optional page number. Example: list_jobs(page=1)",
            "get_job": "Get job details by ID. Example: get_job(job_id=456)",
            "list_inventories": "List inventories with optional name filter. Example: list_inventories(name='prod')",
            "create_inventory": "Create inventory with name, organization ID, and variables. Example: create_inventory(name='web', organization=1, variables={'env': 'prod'})",
            "get_inventory": "Get inventory details by ID. Example: get_inventory(inventory_id=789)",
            "delete_inventory": "Delete inventory by ID. Example: delete_inventory(inventory_id=789)",
            "sync_inventory": "Sync inventory by ID. Example: sync_inventory(inventory_id=789)",
            "list_users": "List all users. Example: list_users()",
            "list_hosts": "List hosts with optional inventory filter. Example: list_hosts(inventory=5)",
            "get_user": "Get user details by ID. Example: get_user(user_id=2)",
            "create_user": "Create user with username and password. Example: create_user(username='john', password='pass123')",
            "update_user": "Update user by ID with new values. Example: update_user(user_id=2, first_name='John')",
            "delete_user": "Delete user by ID. Example: delete_user(user_id=2)",
            "create_job_template": "Create job template with resolved IDs. Example: create_job_template(name='deploy', inventory=5, project=10, playbook='site.yml')",
            "get_project": "Get project details by ID. Example: get_project(project_id=10)",
            "update_project": "Update project by ID. Example: update_project(project_id=10, name='Updated')",
            "delete_project": "Delete project by ID. Example: delete_project(project_id=10)",
            "get_organization": "Get organization details by ID. Example: get_organization(organization_id=2)",
            "update_organization": "Update organization by ID. Example: update_organization(organization_id=2, name='Updated')",
            "delete_organization": "Delete organization by ID. Example: delete_organization(organization_id=2)",
            "list_schedules": "List schedules for template. Example: list_schedules(template_id=123)",
            "create_schedule": "Create schedule for template. Example: create_schedule(template_id=123, name='Daily', rrule='FREQ=DAILY')",
            "get_schedule": "Get schedule details by ID. Example: get_schedule(schedule_id=456)",
            "update_schedule": "Update schedule by ID. Example: update_schedule(schedule_id=456, enabled=false)",
            "delete_schedule": "Delete schedule by ID. Example: delete_schedule(schedule_id=456)",
            "toggle_schedule": "Toggle schedule enabled status. Example: toggle_schedule(schedule_id=456, enabled=true)",
            "list_activity_stream": "List activity stream. Example: list_activity_stream(page=1, page_size=20)",
            "health_check": "Check server health. Example: health_check()",
            "test_connection": "Test connection to server. Example: test_connection()",
            "get_user_by_name": "Get user by username. Example: get_user_by_name(username='admin')",
            "list_projects": "List projects. Example: list_projects(name='web')",
            "create_project": "Create project. Example: create_project(name='app', scm_type='git', scm_url='https://github.com/user/repo')",
            "sync_project": "Sync project. Example: sync_project(project_id=10)",
            "list_organizations": "List organizations. Example: list_organizations(name='DevOps')",
            "create_organization": "Create organization. Example: create_organization(name='New Org')",
            "create_host": "Create host. Example: create_host(host_data={'name': 'web01', 'inventory': 5})",
            "list_credentials": "List credentials. Example: list_credentials()",
            "create_credential": "Create credential. Example: create_credential(name='key', credential_type=1, inputs={'user': 'admin'})",
            "get_credential": "Get credential details. Example: get_credential(credential_id=7)",
            "update_credential": "Update credential. Example: update_credential(credential_id=7, name='Updated')",
            "delete_credential": "Delete credential. Example: delete_credential(credential_id=7)",
            "list_workflow_job_templates": "List workflow templates. Example: list_workflow_job_templates()",
            "create_workflow_job_template": "Create workflow template. Example: create_workflow_job_template(name='Pipeline')",
            "launch_workflow_job_template": "Launch workflow template. Example: launch_workflow_job_template(workflow_job_template_id=8)",
            "update_workflow_job_template": "Update workflow template. Example: update_workflow_job_template(workflow_job_template_id=8, name='Updated')",
            "delete_workflow_job_template": "Delete workflow template. Example: delete_workflow_job_template(workflow_job_template_id=8)",
            "list_notifications": "List notifications. Example: list_notifications()",
            "create_notification": "Create notification. Example: create_notification(name='Alert', notification_type='email', notification_configuration={'recipients': ['admin@example.com']})",
            "get_notification": "Get notification details. Example: get_notification(notification_id=9)",
            "update_notification": "Update notification. Example: update_notification(notification_id=9, name='Updated')",
            "delete_notification": "Delete notification. Example: delete_notification(notification_id=9)",
            "list_instance_groups": "List instance groups. Example: list_instance_groups()",
            "create_instance_group": "Create instance group. Example: create_instance_group(name='High Priority')",
            "get_instance_group": "Get instance group details. Example: get_instance_group(instance_group_id=10)",
            "update_instance_group": "Update instance group. Example: update_instance_group(instance_group_id=10, name='Updated')",
            "delete_instance_group": "Delete instance group. Example: delete_instance_group(instance_group_id=10)",
        }

    def get_optimized_prompt(
        self, tool_name: str, model_name: Optional[str] = None, **kwargs
    ) -> str:
        """Get an optimized prompt for a specific tool based on model capabilities."""
        try:
            # Import here to avoid circular imports
            from app.model_capabilities import should_use_simplified_prompt  # type: ignore[import]

            # Use simplified prompts for smaller models
            if model_name and should_use_simplified_prompt(model_name, tool_name):
                prompts = self.simple_prompts
            else:
                prompts = self.detailed_prompts
        except (ImportError, ModuleNotFoundError):
            # Fallback to detailed prompts if model_capabilities not available
            prompts = self.detailed_prompts

        if tool_name in prompts:
            return prompts[tool_name]
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
            default="http://localhost:31005",
            description="The base URL of MCP server. For K3s deployment, use the NodePort (default: http://localhost:31005). For local Docker, use http://host.docker.internal:8001.",
        )
        mcp_username: str = Field(
            default="openwebui", description="Username for MCP server authentication."
        )
        mcp_password: str = Field(
            default="openwebui", description="Password for MCP server authentication."
        )
        model_name: str = Field(
            default="granite3.1-dense:2b",
            description="Current model name for capability optimization.",
        )
        enable_model_optimization: bool = Field(
            default=True,
            description="Enable model-aware optimizations and simplifications.",
        )

    def __init__(self):
        self.valves = self.Valves()
        self.client = httpx.Client(
            timeout=30.0, auth=(self.valves.mcp_username, self.valves.mcp_password)
        )  # Add timeout and auth for requests
        self.prompt_optimizer = PromptOptimizer()
        self.conversation_id = str(uuid.uuid4())  # Unique conversation ID
        self._context_manager = None
        self._fallback_handler = None
        self._response_simplifier = None

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {"Content-Type": "application/json"}

    @property
    def mcp_server_url(self) -> str:
        return self.valves.mcp_server_url

    @property
    def context_manager(self):
        """Lazy initialization of context manager."""
        if self._context_manager is None:
            try:
                from app.context_manager import context_manager  # type: ignore[import]

                self._context_manager = context_manager
            except (ImportError, ModuleNotFoundError):
                self._context_manager = None
        return self._context_manager

    @property
    def fallback_handler(self):
        """Lazy initialization of fallback handler."""
        if self._fallback_handler is None:
            try:
                from app.fallback_handler import fallback_handler  # type: ignore[import]

                self._fallback_handler = fallback_handler
            except (ImportError, ModuleNotFoundError):
                self._fallback_handler = None
        return self._fallback_handler

    @property
    def response_simplifier(self):
        """Lazy initialization of response simplifier."""
        if self._response_simplifier is None:
            try:
                from app.fallback_handler import response_simplifier  # type: ignore[import]

                self._response_simplifier = response_simplifier
            except (ImportError, ModuleNotFoundError):
                self._response_simplifier = None
        return self._response_simplifier

    def get_optimized_prompt(self, tool_name: str, **kwargs) -> str:
        """Get an optimized prompt for a specific tool."""
        if self.valves.enable_model_optimization:
            return self.prompt_optimizer.get_optimized_prompt(
                tool_name, self.valves.model_name, **kwargs
            )
        else:
            return self.prompt_optimizer.get_optimized_prompt(tool_name, None, **kwargs)

    def get_available_tools(self) -> List[str]:
        """Get available tools based on current model capabilities."""
        if not self.valves.enable_model_optimization:
            # Return all tools if optimization is disabled
            return list(self.prompt_optimizer.detailed_prompts.keys())

        try:
            from app.model_capabilities import get_available_tools  # type: ignore[import]

            return get_available_tools(self.valves.model_name, 0)
        except (ImportError, ModuleNotFoundError):
            return list(self.prompt_optimizer.detailed_prompts.keys())

    def should_simplify_operation(self, operation: str) -> bool:
        """Determine if an operation should be simplified for the current model."""
        if not self.valves.enable_model_optimization:
            return False

        try:
            from app.model_capabilities import should_use_simplified_prompt  # type: ignore[import]

            return should_use_simplified_prompt(self.valves.model_name, operation)
        except (ImportError, ModuleNotFoundError):
            return False

    def log_tool_usage(self, tool_name: str, success: bool, response_time: float):
        """Log tool usage for feedback loop."""
        self.prompt_optimizer.log_tool_usage(tool_name, success, response_time)

        # Track in context manager if available
        if self.context_manager and self.valves.enable_model_optimization:
            context = self.context_manager.get_context(
                self.conversation_id, self.valves.model_name
            )
            # Note: We don't have parameters/result here, so we'll track basic info
            context.add_tool_call(
                tool_name=tool_name,
                parameters={},  # Could be enhanced to track actual parameters
                result={"success": success, "response_time": response_time},
                success=success,
                response_time=response_time,
            )

    def get_all_optimized_prompts(
        self, model_name: Optional[str] = None
    ) -> Dict[str, str]:
        """Get optimized prompts for all available tools based on model."""
        try:
            from app.model_capabilities import get_available_tools  # type: ignore[import]

            available_tools = get_available_tools(
                model_name or "granite3.1-dense:2b", 0
            )

            # Get prompts for available tools
            prompts = {}
            for tool in available_tools:
                prompts[tool] = self.prompt_optimizer.get_optimized_prompt(
                    tool, model_name
                )
            return prompts
        except (ImportError, ModuleNotFoundError):
            # Fallback to all detailed prompts
            return self.prompt_optimizer.detailed_prompts

    def get_conversation_context(self) -> Optional[str]:
        """Get conversation context summary for the current model."""
        if not self.valves.enable_model_optimization or not self.context_manager:
            return None

        context = self.context_manager.get_context(
            self.conversation_id, self.valves.model_name
        )
        return context.get_context_summary()

    def should_use_fallback(self, operation: str) -> bool:
        """Determine if fallback should be used for an operation."""
        if not self.valves.enable_model_optimization or not self.fallback_handler:
            return False

        return self.fallback_handler.should_use_fallback(
            self.valves.model_name, operation
        )

    def simplify_response(self, response: str) -> str:
        """Simplify response for smaller models."""
        if not self.valves.enable_model_optimization or not self.response_simplifier:
            return response

        try:
            # Parse JSON response, simplify, then re-serialize
            parsed = json.loads(response)
            simplified = self.response_simplifier.simplify_response(
                parsed, self.valves.model_name
            )
            return json.dumps(simplified)
        except (json.JSONDecodeError, TypeError):
            # If not JSON or parsing fails, return original
            return response

    def list_templates(self, name: Optional[str] = None) -> str:
        """
        Lists all job templates in AWX, optionally filtered by name.

        :param name: Optional name to filter job templates
        :return: A JSON string containing a list of job templates.

        """
        start_time = time.time()
        success = False

        try:
            url = f"{self.mcp_server_url}/awx/templates"
            params = {}
            if name:
                params["name"] = name

            response = self.client.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            result = json.dumps(response.json())
            success = True

            # Simplify response for smaller models
            result = self.simplify_response(result)

            return result
        except httpx.HTTPStatusError as e:
            error_result = json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
            return error_result
        except Exception as e:
            error_result = json.dumps({"error": str(e)})
            return error_result
        finally:
            # Log tool usage
            response_time = time.time() - start_time
            self.log_tool_usage("list_templates", success, response_time)

    def launch_job_template(
        self, template_id: int, extra_vars: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Launches an AWX job template to start a new job.

        :param template_id: The ID of job template to launch.
        :param extra_vars: A dictionary of extra variables to pass to job.
        :return: A JSON string containing details of newly created job.
        """
        start_time = time.time()
        success = False

        try:
            url = f"{self.mcp_server_url}/awx/job_templates/{template_id}/launch"
            payload: Dict[str, Any] = {}
            if extra_vars:
                payload["extra_vars"] = extra_vars

            response = self.client.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            result = json.dumps(response.json())
            success = True

            # Simplify response for smaller models
            result = self.simplify_response(result)

            return result
        except httpx.HTTPStatusError as e:
            error_result = json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
            return error_result
        except Exception as e:
            error_result = json.dumps({"error": str(e)})
            return error_result
        finally:
            # Log tool usage
            response_time = time.time() - start_time
            self.log_tool_usage("launch_job_template", success, response_time)

    def get_job(self, job_id: int) -> str:
        """
        Retrieves current status and details of a specific job.

        :param job_id: The ID of job to retrieve.
        :return: A JSON string containing status and details of job.
        """
        start_time = time.time()
        success = False

        try:
            url = f"{self.mcp_server_url}/awx/jobs/{job_id}"
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
            result = json.dumps(response.json())
            success = True

            # Simplify response for smaller models
            result = self.simplify_response(result)

            return result
        except httpx.HTTPStatusError as e:
            error_result = json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
            return error_result
        except Exception as e:
            error_result = json.dumps({"error": str(e)})
            return error_result
        finally:
            # Log tool usage
            response_time = time.time() - start_time
            self.log_tool_usage("get_job", success, response_time)

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
        start_time = time.time()
        success = False

        # Check if fallback should be used
        if self.should_use_fallback("create_job_template") and self.fallback_handler:
            fallback_result = self.fallback_handler.execute_with_fallback(
                "create_job_template",
                self.valves.model_name,
                lambda: None,  # Original function would be called here
                name=name,
                inventory=inventory,
                project=project,
                playbook=playbook,
                description=description,
                extra_vars=extra_vars,
            )
            response_time = time.time() - start_time
            self.log_tool_usage(
                "create_job_template", True, response_time
            )  # Assume fallback succeeds
            return json.dumps(fallback_result)

        try:
            url = f"{self.mcp_server_url}/awx/job_templates/"
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
                response = self.client.post(
                    url, headers=self._get_headers(), params=params, json=payload
                )
            else:
                response = self.client.post(
                    url, headers=self._get_headers(), params=params
                )
            response.raise_for_status()
            result = json.dumps(response.json())
            success = True

            # Simplify response for smaller models
            result = self.simplify_response(result)

            return result
        except httpx.HTTPStatusError as e:
            error_result = json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
            return error_result
        except Exception as e:
            error_result = json.dumps({"error": str(e)})
            return error_result
        finally:
            # Log tool usage
            response_time = time.time() - start_time
            self.log_tool_usage("create_job_template", success, response_time)

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
            # Handle empty response body gracefully (common for DELETE operations)
            try:
                return json.dumps(response.json())
            except ValueError:  # JSON parsing error (empty response)
                return json.dumps({"status": "deleted", "id": user_id})
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
        payload: Dict[str, Any] = {}
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

    # Additional methods for complete tool coverage

    def health_check(self) -> str:
        """
        Performs a health check on the AWX connection.

        :return: A JSON string containing health check results.
        """
        url = f"{self.mcp_server_url}/health"
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

    # Credential Management
    def list_credentials(self) -> str:
        """
        Lists credentials in AWX.

        :return: A JSON string containing a list of credentials.
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
        :return: A JSON string containing credential details.
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

    def create_credential(
        self, name: str, credential_type: int, inputs: Dict[str, Any]
    ) -> str:
        """
        Creates a new credential in AWX.

        :param name: Name of the credential.
        :param credential_type: Type ID of the credential.
        :param inputs: Credential inputs.
        :return: A JSON string containing the created credential details.
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
        Updates an existing credential in AWX.

        :param credential_id: The ID of credential to update.
        :param name: Optional new name.
        :param inputs: Optional new inputs.
        :return: A JSON string containing the updated credential details.
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
        Deletes a credential from AWX.

        :param credential_id: The ID of credential to delete.
        :return: A JSON string containing deletion confirmation.
        """
        url = f"{self.mcp_server_url}/awx/credentials/{credential_id}"
        try:
            response = self.client.delete(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps({"status": "deleted", "id": credential_id})
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})

    # Workflow Job Template Management
    def list_workflow_job_templates(self) -> str:
        """
        Lists workflow job templates in AWX.

        :return: A JSON string containing a list of workflow job templates.
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

    def create_workflow_job_template(
        self, name: str, description: Optional[str] = None
    ) -> str:
        """
        Creates a new workflow job template in AWX.

        :param name: Name of the workflow job template.
        :param description: Optional description.
        :return: A JSON string containing the created workflow job template details.
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

    def launch_workflow_job_template(
        self, workflow_job_template_id: int, extra_vars: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Launches a workflow job template in AWX.

        :param workflow_job_template_id: The ID of workflow job template to launch.
        :param extra_vars: Optional extra variables.
        :return: A JSON string containing the launched workflow job details.
        """
        url = f"{self.mcp_server_url}/awx/workflow_job_templates/{workflow_job_template_id}/launch"
        payload = {}
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

    def update_workflow_job_template(
        self,
        workflow_job_template_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> str:
        """
        Updates a workflow job template in AWX.

        :param workflow_job_template_id: The ID of workflow job template to update.
        :param name: Optional new name.
        :param description: Optional new description.
        :return: A JSON string containing the updated workflow job template details.
        """
        url = f"{self.mcp_server_url}/awx/workflow_job_templates/{workflow_job_template_id}"
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

    def delete_workflow_job_template(self, workflow_job_template_id: int) -> str:
        """
        Deletes a workflow job template in AWX.

        :param workflow_job_template_id: The ID of workflow job template to delete.
        :return: A JSON string containing deletion confirmation.
        """
        url = f"{self.mcp_server_url}/awx/workflow_job_templates/{workflow_job_template_id}"
        try:
            response = self.client.delete(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps({"status": "deleted", "id": workflow_job_template_id})
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})

    # Notification Management
    def list_notifications(self) -> str:
        """
        Lists notification templates in AWX.

        :return: A JSON string containing a list of notification templates.
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
        Retrieves details of a specific notification template.

        :param notification_id: The ID of notification template to retrieve.
        :return: A JSON string containing notification template details.
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
        self,
        name: str,
        notification_type: str,
        notification_configuration: Dict[str, Any],
    ) -> str:
        """
        Creates a new notification template in AWX.

        :param name: Name of the notification template.
        :param notification_type: Type of notification.
        :param notification_configuration: Notification configuration.
        :return: A JSON string containing the created notification template details.
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
        Updates a notification template in AWX.

        :param notification_id: The ID of notification template to update.
        :param name: Optional new name.
        :param notification_configuration: Optional new configuration.
        :return: A JSON string containing the updated notification template details.
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
        Deletes a notification template from AWX.

        :param notification_id: The ID of notification template to delete.
        :return: A JSON string containing deletion confirmation.
        """
        url = f"{self.mcp_server_url}/awx/notifications/{notification_id}"
        try:
            response = self.client.delete(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps({"status": "deleted", "id": notification_id})
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})

    # Instance Group Management
    def list_instance_groups(self) -> str:
        """
        Lists instance groups in AWX.

        :return: A JSON string containing a list of instance groups.
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
        :return: A JSON string containing instance group details.
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

        :param name: Name of the instance group.
        :param policy_instance_percentage: Optional policy instance percentage.
        :param policy_instance_minimum: Optional policy instance minimum.
        :return: A JSON string containing the created instance group details.
        """
        url = f"{self.mcp_server_url}/awx/instance_groups"
        payload: Dict[str, Any] = {"name": name}
        if policy_instance_percentage is not None:
            payload["policy_instance_percentage"] = policy_instance_percentage
        if policy_instance_minimum is not None:
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
        :param name: Optional new name.
        :param policy_instance_percentage: Optional new policy percentage.
        :param policy_instance_minimum: Optional new policy minimum.
        :return: A JSON string containing the updated instance group details.
        """
        url = f"{self.mcp_server_url}/awx/instance_groups/{instance_group_id}"
        payload: Dict[str, Any] = {}
        if name:
            payload["name"] = name
        if policy_instance_percentage is not None:
            payload["policy_instance_percentage"] = policy_instance_percentage
        if policy_instance_minimum is not None:
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
        Deletes an instance group from AWX.

        :param instance_group_id: The ID of instance group to delete.
        :return: A JSON string containing deletion confirmation.
        """
        url = f"{self.mcp_server_url}/awx/instance_groups/{instance_group_id}"
        try:
            response = self.client.delete(url, headers=self._get_headers())
            response.raise_for_status()
            return json.dumps({"status": "deleted", "id": instance_group_id})
        except httpx.HTTPStatusError as e:
            return json.dumps(
                {
                    "error": f"HTTP error occurred: {e.response.status_code}",
                    "detail": e.response.text,
                }
            )
        except Exception as e:
            return json.dumps({"error": str(e)})
