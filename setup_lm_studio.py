# setup_lm_studio.py
import json
import os


def create_lm_studio_config(base_url: str, output_path: str = "~/.lmstudio/mcp.json"):
    """
    Creates a configuration file for LM Studio to integrate with the AWX MCP server.

    Args:
        base_url (str): The base URL of the AWX MCP server.
        output_path (str, optional): The path to save the configuration file. Defaults to "~/.lmstudio/mcp.json".
    """
    mcp_server_path = os.environ.get(
        "MCP_SERVER_PATH", os.path.join(os.path.dirname(__file__), "mcp_server.py")
    )
    awx_base_url = os.environ.get("AWX_BASE_URL", base_url)

    config = {
        "mcpServers": {
            "awx-mcp-server": {
                "command": "python3",
                "args": [mcp_server_path, awx_base_url],
                "cwd": os.path.dirname(__file__),
                "description": "AWX MCP Server Bridge",
                "capabilities": ["tools", "resources"],
            }
        }
    }

    # Expand the tilde to the user's home directory
    output_path = os.path.expanduser(output_path)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"LM Studio configuration file created at: {output_path}")


if __name__ == "__main__":
    # Example usage:
    awx_base_url = "http://localhost:8001"  # Replace with your AWX base URL
    create_lm_studio_config(awx_base_url)
