from superagi.helper.json_cleaner import JsonCleaner
import pytest

def test_extract_json_section():
    test_str = 'Before json {"key":"value"} after json'
    result = JsonCleaner.extract_json_section(test_str)
    assert result == '{"key":"value"}'

def test_remove_escape_sequences():
    test_str = r'This is a test\nstring'
    result = JsonCleaner.remove_escape_sequences(test_str)
    assert result == 'This is a test\nstring'

def test_balance_braces():
    test_str = '{{{{"key":"value"}}'
    result = JsonCleaner.balance_braces(test_str)
    assert result == '{{{{"key":"value"}}}}'


def test_balance_braces():
    test_str = '{"key": false}'
    result = JsonCleaner.clean_boolean(test_str)
    assert result == '{"key": False}'

