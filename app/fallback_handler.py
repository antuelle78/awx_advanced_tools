# Fallback mechanisms for complex operations on smaller models

from typing import Dict, Any, Callable


class FallbackHandler:
    """Handles fallback logic for complex operations on smaller models."""

    def __init__(self):
        self.fallbacks = self._load_fallbacks()

    def _load_fallbacks(self) -> Dict[str, Callable]:
        """Load fallback functions for complex operations."""
        return {
            "create_job_template": self._create_job_template_fallback,
            "create_workflow_job_template": self._create_workflow_fallback,
            "create_credential": self._create_credential_fallback,
            "launch_workflow_job_template": self._launch_workflow_fallback,
        }

    def should_use_fallback(self, model_name: str, operation: str) -> bool:
        """Determine if a fallback should be used for an operation."""
        try:
            from app.model_capabilities import COMPLEX_TOOLS, get_model_capabilities
            capabilities = get_model_capabilities(model_name)

            # Use fallback for complex tools on smaller models
            if operation in COMPLEX_TOOLS and capabilities.max_tools <= 15:
                return True

            # Use fallback if model has poor JSON accuracy
            if capabilities.json_accuracy == "low":
                return True

            return False
        except ImportError:
            return False

    def execute_with_fallback(self, operation: str, model_name: str,
                            original_func: Callable, *args, **kwargs) -> Any:
        """Execute operation with fallback if needed."""
        if self.should_use_fallback(model_name, operation):
            fallback_func = self.fallbacks.get(operation)
            if fallback_func:
                return fallback_func(*args, **kwargs)

        # Use original function
        return original_func(*args, **kwargs)

    def _create_job_template_fallback(self, name: str, inventory: int, project: int,
                                    playbook: str, **kwargs) -> Dict[str, Any]:
        """Simplified fallback for creating job templates."""
        # Break complex operation into simpler steps
        steps = [
            f"First, verify inventory {inventory} exists",
            f"Then verify project {project} exists",
            f"Create job template '{name}' with playbook '{playbook}'",
            "Set basic configuration (no extra vars for simplicity)"
        ]

        return {
            "fallback_used": True,
            "operation": "create_job_template",
            "steps": steps,
            "estimated_complexity": "medium",
            "recommendation": "Use the API directly or break into smaller operations"
        }

    def _create_workflow_fallback(self, name: str, **kwargs) -> Dict[str, Any]:
        """Simplified fallback for creating workflow templates."""
        return {
            "fallback_used": True,
            "operation": "create_workflow_job_template",
            "steps": [
                f"Prepare to create workflow '{name}'",
                "Note: Workflow creation is complex for smaller models",
                "Consider using existing workflows instead"
            ],
            "estimated_complexity": "high",
            "recommendation": "Use existing workflow templates or create manually via UI"
        }

    def _create_credential_fallback(self, name: str, credential_type: int,
                                  inputs: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Simplified fallback for creating credentials."""
        return {
            "fallback_used": True,
            "operation": "create_credential",
            "steps": [
                f"Prepare credential '{name}' of type {credential_type}",
                "Credential inputs provided but creation is complex",
                "Consider using existing credentials"
            ],
            "estimated_complexity": "high",
            "recommendation": "Create credentials manually via AWX UI for security"
        }

    def _launch_workflow_fallback(self, workflow_id: int, **kwargs) -> Dict[str, Any]:
        """Simplified fallback for launching workflows."""
        return {
            "fallback_used": True,
            "operation": "launch_workflow_job_template",
            "steps": [
                f"Prepare to launch workflow {workflow_id}",
                "Workflow launching requires careful parameter handling",
                "Consider using job templates instead for simpler operations"
            ],
            "estimated_complexity": "high",
            "recommendation": "Use individual job templates for critical operations"
        }

    def get_simplified_instructions(self, operation: str) -> str:
        """Get simplified instructions for complex operations."""
        instructions = {
            "create_job_template": """
            Creating job templates requires multiple steps:
            1. Verify inventory and project exist
            2. Provide basic template information
            3. Test the template before using in production

            For smaller models, consider using existing templates instead.
            """,

            "create_workflow_job_template": """
            Workflow creation is complex and involves multiple interconnected jobs.
            For smaller models, this operation may not work reliably.

            Recommendation: Use existing workflows or create simple job templates.
            """,

            "create_credential": """
            Credential creation involves sensitive security information.
            For smaller models, this operation has higher risk of errors.

            Recommendation: Create credentials manually through the AWX web interface.
            """,

            "launch_workflow_job_template": """
            Workflow launching involves complex parameter passing and job orchestration.
            For smaller models, this may not execute reliably.

            Recommendation: Use individual job templates for critical operations.
            """
        }

        return instructions.get(operation, f"Operation '{operation}' is complex for smaller models.")


class ResponseSimplifier:
    """Simplifies API responses for smaller models."""

    def __init__(self):
        self.max_response_length = 1000
        self.max_list_items = 10

    def simplify_response(self, response: Any, model_name: str) -> Any:
        """Simplify response based on model capabilities."""
        try:
            from app.model_capabilities import get_model_capabilities
            capabilities = get_model_capabilities(model_name)

            # Simplify for smaller models
            if capabilities.max_tools <= 10:
                return self._aggressively_simplify(response)
            elif capabilities.max_tools <= 20:
                return self._moderately_simplify(response)
            else:
                return response

        except ImportError:
            return self._moderately_simplify(response)

    def _aggressively_simplify(self, response: Any) -> Any:
        """Aggressive simplification for very small models."""
        if isinstance(response, dict):
            # Keep only essential fields
            essential_keys = ['id', 'name', 'status', 'result', 'count']
            simplified = {k: v for k, v in response.items() if k in essential_keys}

            # Truncate long values
            for k, v in simplified.items():
                if isinstance(v, str) and len(v) > 100:
                    simplified[k] = v[:100] + "..."

            return simplified

        elif isinstance(response, list):
            # Limit list items
            return response[:5] if len(response) > 5 else response

        return response

    def _moderately_simplify(self, response: Any) -> Any:
        """Moderate simplification for medium models."""
        if isinstance(response, dict):
            # Truncate very long values
            simplified = {}
            for k, v in response.items():
                if isinstance(v, str) and len(v) > 200:
                    simplified[k] = v[:200] + "..."
                else:
                    simplified[k] = v
            return simplified

        elif isinstance(response, list):
            # Moderate list limiting
            return response[:self.max_list_items] if len(response) > self.max_list_items else response

        return response


# Global instances
fallback_handler = FallbackHandler()
response_simplifier = ResponseSimplifier()