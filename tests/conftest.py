# tests/conftest.py
# This file sets up environment variables for tests

import os

# Set environment variables for tests
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["AUDIT_LOG_DIR"] = "/tmp/audit"
