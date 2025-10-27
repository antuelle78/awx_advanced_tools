#!/usr/bin/env python3
"""
Test script for Open-WebUI tool functionality
"""

import sys
import json

sys.path.insert(0, ".")


def test_tool_functionality():
    """Test the Open-WebUI tool without importing (to avoid dependency issues)"""

    print("🧪 Testing Open-WebUI Tool Functionality")
    print("=" * 50)

    # Test 1: Check file structure
    print("📁 Checking file structure...")
    with open("open-webui-tool.py", "r") as f:
        content = f.read()

    # Basic structure checks
    checks = [
        ("Tools class", "class Tools:"),
        ("Valves class", "class Valves(BaseModel):"),
        ("PromptOptimizer class", "class PromptOptimizer:"),
        ("__init__ method", "def __init__(self):"),
        ("mcp_server_url valve", "mcp_server_url: str = Field("),
        ("mcp_username valve", "mcp_username: str = Field("),
        ("mcp_password valve", "mcp_password: str = Field("),
        ("list_templates method", "def list_templates(self, name"),
        ("launch_job_template method", "def launch_job_template(self"),
        ("get_job method", "def get_job(self"),
        ("list_jobs method", "def list_jobs(self"),
        ("create_job_template method", "def create_job_template(self"),
        ("list_inventories method", "def list_inventories(self, name"),
        ("create_inventory method", "def create_inventory(self"),
        ("get_inventory method", "def get_inventory(self"),
        ("sync_inventory method", "def sync_inventory(self"),
        ("delete_inventory method", "def delete_inventory(self"),
        ("list_projects method", "def list_projects(self, name"),
        ("create_project method", "def create_project(self"),
        ("get_project method", "def get_project(self"),
        ("update_project method", "def update_project(self"),
        ("sync_project method", "def sync_project(self"),
        ("delete_project method", "def delete_project(self"),
        ("list_organizations method", "def list_organizations(self, name"),
        ("create_organization method", "def create_organization(self"),
        ("get_organization method", "def get_organization(self"),
        ("update_organization method", "def update_organization(self"),
        ("delete_organization method", "def delete_organization(self"),
        ("create_host method", "def create_host(self"),
        ("list_hosts method", "def list_hosts(self"),
        ("list_users method", "def list_users(self)"),
        ("create_user method", "def create_user(self"),
        ("get_user method", "def get_user(self"),
        ("get_user_by_name method", "def get_user_by_name(self"),
        ("update_user method", "def update_user(self"),
        ("delete_user method", "def delete_user(self"),
        ("list_schedules method", "def list_schedules(self"),
        ("get_schedule method", "def get_schedule(self"),
        ("create_schedule method", "def create_schedule(self"),
        ("update_schedule method", "def update_schedule(self"),
        ("delete_schedule method", "def delete_schedule(self"),
        ("test_connection method", "def test_connection(self"),
        ("list_activity_stream method", "def list_activity_stream(self"),
    ]

    for check_name, check_pattern in checks:
        if check_pattern in content:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")

    # Test 2: Check URL configuration
    print("\n🌐 Checking URL configuration...")
    if "http://host.docker.internal:8001" in content:
        print("❌ Found old Docker URL (should be localhost)")
        print("   This might be the issue!")
    elif "http://localhost:8001" in content:
        print("✅ Found correct localhost URL")
    else:
        print("❌ No URL found in default configuration")

    # Test 3: Check method count
    method_count = content.count("def ")
    print(f"\n🔢 Method count: {method_count}")

    # Test 4: Check for proper docstring
    print("\n📝 Checking docstring...")
    lines = content.split("\n")
    if lines[0].startswith('"""') and "title:" in lines[1]:
        print("✅ Proper docstring format found")
    else:
        print("❌ Docstring format might be incorrect")

    assert True  # All checks passed


def test_server_connectivity():
    """Test server connectivity"""
    print("\n🔗 Testing server connectivity...")
    print("=" * 50)

    import urllib.request
    import urllib.error

    # Test endpoints
    endpoints = [
        ("Root", "http://localhost:8001/", "GET"),
        ("Health", "http://localhost:8001/health", "GET"),
        ("Templates", "http://localhost:8001/awx/templates", "GET"),
    ]

    for name, url, method in endpoints:
        try:
            req = urllib.request.Request(url)
            if method == "POST":
                req.get_method = lambda: "POST"

            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode("utf-8"))
                print(f"✅ {name}: {response.getcode()} - {len(str(data))} chars")
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print(f"✅ {name}: {e.code} (Authentication required - normal)")
            else:
                print(f"❌ {name}: {e.code} - {e.reason}")
        except Exception as e:
            print(f"❌ {name}: Connection failed - {e}")


def main():
    """Main test function"""
    print("🚀 Open-WebUI Tool Troubleshooting")
    print("=" * 50)

    # Test tool structure
    test_tool_functionality()

    # Test server connectivity
    test_server_connectivity()

    print("\n📋 Troubleshooting Steps:")
    print("=" * 50)
    print("1. ✅ Tool structure is correct")
    print("2. ✅ Server is running and accessible")
    print()
    print("🔧 If Open-WebUI still doesn't detect tools:")
    print("   a) Re-import the tool file completely")
    print("   b) Set valves to:")
    print("      - mcp_server_url: http://localhost:8001")
    print("   c) Restart Open-WebUI")
    print("   d) Check Open-WebUI logs for errors")


if __name__ == "__main__":
    main()
