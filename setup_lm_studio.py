#!/usr/bin/env python3
"""
LM Studio Integration Setup Script

This script helps set up the integration between your AWX MCP server and LM Studio.
It provides utilities for testing the connection and generating configurations.
"""

import json
import os


def test_awx_connection(base_url: str) -> bool:
    """Test connection to AWX server"""
    import httpx

    try:
        response = httpx.get(f"{base_url}/awx/templates", timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False


def create_lm_studio_config(base_url: str, output_path: str = "~/.lmstudio/mcp.json"):
    """Create LM Studio MCP configuration"""

    config = {
        "mcpServers": {
            "awx-mcp": {
                "url": base_url,
                "description": "AWX Management via REST API",
                "capabilities": ["tools", "resources"],
                "tools": [
                    {
                        "name": "launch_job_template",
                        "description": "Launch an AWX job template",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "template_id": {
                                    "type": "integer",
                                    "description": "Job template ID",
                                },
                                "extra_vars": {
                                    "type": "object",
                                    "description": "Extra variables",
                                },
                            },
                            "required": ["template_id"],
                        },
                    },
                    {
                        "name": "get_job_status",
                        "description": "Get AWX job status",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "job_id": {"type": "integer", "description": "Job ID"}
                            },
                            "required": ["job_id"],
                        },
                    },
                    {
                        "name": "list_templates",
                        "description": "List AWX job templates",
                        "parameters": {"type": "object", "properties": {}},
                    },
                    {
                        "name": "list_inventories",
                        "description": "List AWX inventories",
                        "parameters": {"type": "object", "properties": {}},
                    },
                    {
                        "name": "list_jobs",
                        "description": "List AWX jobs",
                        "parameters": {
                            "type": "object",
                            "properties": {"page": {"type": "integer", "default": 1}},
                        },
                    },
                ],
                "resources": [
                    {
                        "uri": "awx://templates",
                        "name": "Job Templates",
                        "description": "Available AWX job templates",
                        "mimeType": "application/json",
                    },
                    {
                        "uri": "awx://inventories",
                        "name": "Inventories",
                        "description": "AWX inventories",
                        "mimeType": "application/json",
                    },
                    {
                        "uri": "awx://jobs",
                        "name": "Jobs",
                        "description": "AWX jobs",
                        "mimeType": "application/json",
                    },
                ],
            }
        }
    }

    # Expand path
    output_path = os.path.expanduser(output_path)

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write configuration
    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ LM Studio configuration created: {output_path}")
    return True


def main():
    """Main setup function"""
    print("🔧 LM Studio Integration Setup")
    print("=" * 50)

    # Check if server is running
    base_url = "http://localhost:8001"
    print(f"📍 Using AWX server URL: {base_url}")

    # Test connection
    print("🔗 Testing AWX connection...")
    if test_awx_connection(base_url):
        print("✅ AWX server connection successful!")
    else:
        print("❌ AWX server connection failed!")
        print("   Make sure the server is running: docker compose up -d")
        return

    # Create LM Studio config
    print("📝 Creating LM Studio configuration...")
    config_path = "~/.lmstudio/mcp.json"
    if create_lm_studio_config(base_url, config_path):
        print("✅ Configuration created successfully!")
        print()
        print("🚀 Next Steps:")
        print("1. Close LM Studio completely")
        print("2. Restart LM Studio")
        print("3. The AWX tools should appear in the MCP tools section")
        print("4. Test by asking: 'List all job templates in AWX'")
        print()
        print("📚 See LM_STUDIO_INTEGRATION.md for detailed instructions")
    else:
        print("❌ Failed to create configuration")


if __name__ == "__main__":
    main()
