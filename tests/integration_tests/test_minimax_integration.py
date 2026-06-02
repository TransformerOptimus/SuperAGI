"""
Integration test for MiniMax LLM provider.

This test verifies end-to-end MiniMax chat completion using the real API.
Requires MINIMAX_API_KEY environment variable to be set.
Skip with: pytest -m "not integration"
"""
import os
import pytest

from superagi.llms.minimax import MiniMax


@pytest.mark.skipif(
    not os.environ.get("MINIMAX_API_KEY"),
    reason="MINIMAX_API_KEY not set"
)
class TestMiniMaxIntegration:
    def setup_method(self):
        self.api_key = os.environ["MINIMAX_API_KEY"]

    def test_chat_completion_m3(self):
        minimax = MiniMax(api_key=self.api_key, model="MiniMax-M3")
        messages = [{"role": "user", "content": "Say hello in one word."}]
        result = minimax.chat_completion(messages, max_tokens=50)
        assert "error" not in result
        assert "content" in result
        assert len(result["content"]) > 0

    def test_chat_completion_m27(self):
        minimax = MiniMax(api_key=self.api_key, model="MiniMax-M2.7")
        messages = [{"role": "user", "content": "Say hello in one word."}]
        result = minimax.chat_completion(messages, max_tokens=50)
        assert "error" not in result
        assert "content" in result
        assert len(result["content"]) > 0

    def test_chat_completion_m27_highspeed(self):
        minimax = MiniMax(api_key=self.api_key, model="MiniMax-M2.7-highspeed")
        messages = [{"role": "user", "content": "What is 2+2? Reply with just the number."}]
        result = minimax.chat_completion(messages, max_tokens=50)
        assert "error" not in result
        assert "content" in result
        assert "4" in result["content"]

    def test_verify_access_key(self):
        minimax = MiniMax(api_key=self.api_key)
        assert minimax.verify_access_key() is True

    def test_verify_access_key_invalid(self):
        minimax = MiniMax(api_key="sk-invalid-key")
        assert minimax.verify_access_key() is False
