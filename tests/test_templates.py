from app.llm.templates import TEMPLATES, LAUNCH_JOB_TEMPLATE, VALIDATE_SCHEMA_TEMPLATE


class TestTemplates:
    def test_launch_job_template_format(self):
        payload = {"template_id": 1, "extra_vars": {"key": "value"}}
        prompt = LAUNCH_JOB_TEMPLATE.format(**payload)
        assert "template_id" in prompt
        assert "extra_vars" in prompt
        assert "Think step-by-step" in prompt
        assert "Only return a JSON object" in prompt

    def test_validate_schema_template_format(self):
        payload = {"payload": '{"name": "test"}', "schema": '{"type": "object"}'}
        prompt = VALIDATE_SCHEMA_TEMPLATE.format(**payload)
        assert "JSON payload" in prompt
        assert "Think step-by-step" in prompt
        assert "Only return a JSON object" in prompt

    def test_templates_dict(self):
        assert "launch_job_template" in TEMPLATES
        assert "validate_schema" in TEMPLATES
        assert "summarize_log" in TEMPLATES
        assert "get_awx_status" in TEMPLATES
        assert "create_project" in TEMPLATES

    def test_template_consistency(self):
        for action, template in TEMPLATES.items():
            assert "Think step-by-step" in template
            assert "Only return a JSON object" in template
            assert '{"result":' in template
