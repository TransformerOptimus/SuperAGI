import sys
from unittest.mock import MagicMock

sys.modules["superagi.llms.hugging_face"] = MagicMock()
sys.modules["superagi.config.config"] = MagicMock()

from superagi.helper.models_helper import is_safe_url


def test_safe_url_valid():
    assert is_safe_url("https://example.com") is True


def test_safe_url_localhost():
    assert is_safe_url("http://127.0.0.1") is False


def test_safe_url_internal_ip():
    assert is_safe_url("http://192.168.1.1") is False


def test_safe_url_file_scheme():
    assert is_safe_url("file:///etc/passwd") is False