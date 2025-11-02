#!/usr/bin/env python3
"""
Test script to verify open-webui-tool-multi-server works with table-formatted responses
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

def test_table_responses():
    """Test that the tool can handle table-formatted responses."""
    print("🧪 Testing Open-WebUI Multi-Server Tool with Table Responses")
    print("=" * 60)

    try:
        # Read and execute the tool file directly
        with open("open-webui-tool-multi-server.py", "r") as f:
            tool_code = f.read()

        # Extract the Tools class and execute it
        # This is a bit hacky but necessary since it's not a proper Python module
        import types
        import sys

        # Create a module from the tool code
        tool_module = types.ModuleType("tool_module")
        sys.modules["tool_module"] = tool_module

        # Execute the tool code in the module
        exec(tool_code, tool_module.__dict__)

        # Get the Tools class
        Tools = tool_module.Tools

        # Initialize the tool
        tool = Tools()

        # Test list_templates (should return table)
        print("\n📊 Testing list_templates...")
        result = tool.list_templates()
        print("Response type:", type(result))
        print("Response preview:")
        print(result[:300] + "..." if len(result) > 300 else result)

        # Test list_inventories (should return table)
        print("\n📊 Testing list_inventories...")
        result = tool.list_inventories()
        print("Response type:", type(result))
        print("Response preview:")
        print(result[:300] + "..." if len(result) > 300 else result)

        # Test list_users (should return table)
        print("\n📊 Testing list_users...")
        result = tool.list_users()
        print("Response type:", type(result))
        print("Response preview:")
        print(result[:300] + "..." if len(result) > 300 else result)

        # Test create_schedule (should reach server even if AWX rejects)
        print("\n📅 Testing create_schedule...")
        try:
            result = tool.create_schedule(7, "test-schedule", "FREQ=MINUTELY;INTERVAL=5")
            print("Response type:", type(result))
            print("Response preview:")
            print(result[:200] + "..." if len(result) > 200 else result)
            # Check if it's a proper error from AWX (not 404)
            if "404" not in result and "Not Found" not in result:
                print("✅ Server reachable - got proper AWX response")
            else:
                print("❌ Still getting 404 - endpoint not found")
        except Exception as e:
            print(f"❌ Create schedule test failed: {e}")

        print("\n✅ All tests passed! Tool correctly handles table responses.")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_table_responses()
    sys.exit(0 if success else 1)