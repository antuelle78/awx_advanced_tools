# tests/conftest.py
# This file sets up a dummy openai module for tests and patches environment variables

import os
import sys

# Set LLM_PROVIDER to ollama to avoid import errors
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["AUDIT_LOG_DIR"] = "/tmp/audit"

# Create a dummy openai module with minimal ChatCompletion
class DummyChatCompletion:
    async def acreate(self, **kwargs):
        # Return a dummy response that mimics OpenAI's API
        class DummyMessage:
            def __init__(self):
                self.content = '{"result": "ok"}'

        class DummyChoice:
            def __init__(self):
                self.message = DummyMessage()

        class DummyResponse:
            def __init__(self):
                self.choices = [DummyChoice()]

        return DummyResponse()

# Add dummy openai to sys.modules
sys.modules["openai"] = type(sys)('openai')
sys.modules["openai"].ChatCompletion = DummyChatCompletion
