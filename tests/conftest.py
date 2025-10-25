# tests/conftest.py
# This file sets up a dummy openai module for tests and patches environment variables


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

        return """???"""
