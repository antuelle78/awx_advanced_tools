import json
import tempfile
from unittest.mock import patch, mock_open
from app.audit.logger import audit


class TestAuditLogger:
    @patch("app.audit.logger.settings")
    @patch("app.audit.logger.datetime")
    @patch("builtins.open", new_callable=mock_open)
    def test_audit_success(self, mock_file, mock_datetime, mock_settings):
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_settings.audit_log_dir = temp_dir
            mock_datetime.utcnow.return_value.isoformat.return_value = (
                "2023-01-01T00:00:00Z"
            )
            mock_datetime.utcnow.return_value.strftime.return_value = "20230101"

            audit("user1", "launch_job", "AWX", {"template_id": 1}, {"job_id": 123})

            mock_file.assert_called_once_with(
                f"{temp_dir}/audit_20230101.log", "a", encoding="utf-8"
            )
            handle = mock_file()
            handle.write.assert_called_once()
            written = handle.write.call_args[0][0]
            entry = json.loads(written.strip())
            assert entry["user"] == "user1"
            assert entry["action"] == "launch_job"
            assert entry["platform"] == "AWX"
            assert entry["request"] == {"template_id": 1}
            assert entry["response"] == {"job_id": 123}
            assert entry["error"] is None

    @patch("app.audit.logger.settings")
    @patch("app.audit.logger.datetime")
    @patch("builtins.open", new_callable=mock_open)
    def test_audit_with_error(self, mock_file, mock_datetime, mock_settings):
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_settings.audit_log_dir = temp_dir
            mock_datetime.utcnow.return_value.isoformat.return_value = (
                "2023-01-01T00:00:00Z"
            )
            mock_datetime.utcnow.return_value.strftime.return_value = "20230101"

            audit(
                "user1", "launch_job", "AWX", {"template_id": 1}, error="Error message"
            )

            handle = mock_file()
            written = handle.write.call_args[0][0]
            entry = json.loads(written.strip())
            assert entry["error"] == "Error message"
            assert entry["response"] is None
