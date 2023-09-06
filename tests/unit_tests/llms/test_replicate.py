import os
from unittest.mock import patch
import pytest
import requests
from unittest import TestCase
from superagi.llms.replicate import Replicate
from superagi.config.config import get_config

class TestReplicate(TestCase):

    @patch('os.environ')
    @patch('replicate.run')
    def test_chat_completion(self, mock_replicate_run, mock_os_environ):
        # Arrange
        api_key = 'test_api_key'
        model = 'test_model'
        version = 'test_version'
        max_length=1000
        temperature=0.7
        candidate_count=1
        top_k=40
        top_p=0.95
        rep_instance = Replicate(api_key, model=model, version=version, max_length=max_length, temperature=temperature,
                         candidate_count=candidate_count, top_k=top_k, top_p=top_p)
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        mock_replicate_run.return_value = iter(['Sure, I can help with that.'])

        # Act
        result = rep_instance.chat_completion(messages)

        # Assert
        assert result == {"response": ['Sure, I can help with that.'], "content": 'Sure, I can help with that.'}

    @patch.object(requests, "get")
    def test_verify_access_key(self, mock_get):
        # Arrange
        api_key = 'test_api_key'
        model = 'test_model'
        version = 'test_version'
        rep_instance = Replicate(api_key, model=model, version=version)
        mock_get.return_value.status_code = 200

        # Act
        result = rep_instance.verify_access_key()

        # Assert
        assert result is True
        mock_get.assert_called_with("https://api.replicate.com/v1/collections", headers={"Authorization": "Token " + api_key})

    @patch.object(requests, "get")
    def test_verify_access_key_false(self, mock_get):
        # Arrange
        api_key = 'test_api_key'
        model = 'test_model'
        version = 'test_version'
        rep_instance = Replicate(api_key, model=model, version=version)
        mock_get.return_value.status_code = 400

        # Act
        result = rep_instance.verify_access_key()

        # Assert
        assert result is False