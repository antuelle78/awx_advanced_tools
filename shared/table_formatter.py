# Table formatting utilities for consistent LLM output
import json
from typing import Dict, Any, Optional
from datetime import datetime


class TableFormatter:
    """Utility for formatting AWX API responses as markdown tables."""

    # Standard column definitions for each resource type
    RESOURCE_COLUMNS = {
        "job_templates": ["ID", "Name", "Description", "Created", "Modified"],
        "jobs": ["ID", "Name", "Status", "Started", "Finished"],
        "inventories": ["ID", "Name", "Organization", "Hosts Count", "Groups Count"],
        "users": ["ID", "Username", "First Name", "Last Name", "Email"],
        "projects": ["ID", "Name", "SCM Type", "SCM URL", "Status"],
        "organizations": ["ID", "Name", "Description", "Created", "Modified"],
        "schedules": ["ID", "Name", "Template", "RRULE", "Enabled"],
        "credentials": ["ID", "Name", "Type", "Created", "Modified"],
        "hosts": ["ID", "Name", "Inventory", "Enabled", "Variables"],
        "notifications": ["ID", "Name", "Type", "Created", "Modified"],
        "instance_groups": ["ID", "Name", "Policy", "Created", "Modified"],
        "workflow_job_templates": ["ID", "Name", "Description", "Created", "Modified"],
    }

    @staticmethod
    def _format_datetime(dt_str: Optional[str]) -> str:
        """Format datetime string for display."""
        if not dt_str:
            return "N/A"
        try:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, Exception):
            return dt_str[:19] if dt_str else "N/A"

    @staticmethod
    def _truncate_text(text: Optional[str], max_length: int = 50) -> str:
        """Truncate text to max length with ellipsis."""
        if not text:
            return "N/A"
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

    @staticmethod
    def format_list_response(data: Dict[str, Any], resource_type: str) -> str:
        """Format paginated list responses as markdown tables."""
        if not isinstance(data, dict) or "results" not in data:
            return TableFormatter.format_single_item(data, resource_type)

        results = data["results"]
        if not results:
            return f"| No {resource_type.replace('_', ' ')} found |\n|{'-'*30}|"

        columns = TableFormatter.RESOURCE_COLUMNS.get(resource_type, ["ID", "Name", "Created"])

        # Build table header
        header = "| " + " | ".join(columns) + " |"
        separator = "|" + "|".join(["-" * (len(col) + 2) for col in columns]) + "|"

        rows = [header, separator]

        # Add data rows
        for item in results:
            row_data = []
            for col in columns:
                col_lower = col.lower().replace(" ", "_")
                value = item.get(col_lower, item.get(col, "N/A"))

                # Format specific column types
                if "created" in col_lower or "modified" in col_lower or "started" in col_lower or "finished" in col_lower:
                    value = TableFormatter._format_datetime(value)
                elif col_lower in ["description", "scm_url", "rrule", "variables"]:
                    value = TableFormatter._truncate_text(str(value))
                elif isinstance(value, bool):
                    value = "Yes" if value else "No"
                else:
                    value = str(value) if value is not None else "N/A"

                row_data.append(value)

            row = "| " + " | ".join(row_data) + " |"
            rows.append(row)

        # Add summary if there are more results
        count = data.get("count", len(results))
        if count > len(results):
            rows.append(f"| ... and {count - len(results)} more {resource_type.replace('_', ' ')}(s) |")

        return "\n".join(rows)

    @staticmethod
    def format_single_item(data: Dict[str, Any], resource_type: str) -> str:
        """Format single item details as a table."""
        if not isinstance(data, dict):
            return f"| Value |\n|-------|\n| {str(data)} |"

        # For single items, show key-value pairs
        header = "| Property | Value |"
        separator = "|----------|-------|"

        rows = [header, separator]

        for key, value in data.items():
            # Format the key for display
            display_key = key.replace("_", " ").title()

            # Format the value
            if isinstance(value, dict):
                formatted_value = json.dumps(value, indent=2)[:100] + "..." if len(json.dumps(value)) > 100 else json.dumps(value)
            elif isinstance(value, list):
                formatted_value = f"{len(value)} items" if len(value) > 3 else str(value)
            elif isinstance(value, bool):
                formatted_value = "Yes" if value else "No"
            elif key in ["created", "modified", "started", "finished"]:
                formatted_value = TableFormatter._format_datetime(str(value))
            else:
                formatted_value = TableFormatter._truncate_text(str(value))

            rows.append(f"| {display_key} | {formatted_value} |")

        return "\n".join(rows)

    @staticmethod
    def format_operation_result(operation: str, success: bool, data: Optional[Dict[str, Any]] = None, error: Optional[str] = None) -> str:
        """Format operation results (create/update/delete) as a table."""
        status = "Success" if success else "Failed"

        header = "| Operation | Status | Details |"
        separator = "|-----------|--------|---------|"

        rows = [header, separator]

        if success and data:
            # Show created/updated resource info
            if isinstance(data, dict) and "id" in data:
                details = f"ID: {data['id']}, Name: {data.get('name', 'N/A')}"
            else:
                details = "Operation completed"
        elif error:
            details = TableFormatter._truncate_text(error, 80)
        else:
            details = "Operation completed"

        rows.append(f"| {operation.title()} | {status} | {details} |")

        return "\n".join(rows)

    @staticmethod
    def format_error(error_message: str, server: str = "Unknown") -> str:
        """Format error messages as a table."""
        header = "| Error | Server | Details |"
        separator = "|-------|--------|---------|"

        rows = [header, separator]
        rows.append(f"| Error | {server} | {TableFormatter._truncate_text(error_message, 80)} |")

        return "\n".join(rows)