from superagi.helper.json_cleaner import JsonCleaner
import pytest

def test_preprocess_json_input():
    test_str = r'This is a test\ string'
    result = JsonCleaner.preprocess_json_input(test_str)
    assert result == r'This is a test\\ string'

def test_extract_json_section():
    test_str = 'Before json {"key":"value"} after json'
    result = JsonCleaner.extract_json_section(test_str)
    assert result == '{"key":"value"}'

def test_remove_escape_sequences():
    test_str = r'This is a test\nstring'
    result = JsonCleaner.remove_escape_sequences(test_str)
    assert result == 'This is a test\nstring'

def test_add_quotes_to_property_names():
    test_str = '{key: "value"}'
    result = JsonCleaner.add_quotes_to_property_names(test_str)
    assert result == '{"key": "value"}'

def test_balance_braces():
    test_str = '{{{{"key":"value"}}'
    result = JsonCleaner.balance_braces(test_str)
    assert result == '{{{{"key":"value"}}}}'

def test_check_and_clean_json():
    test_str = r'{key: "value"\n}'
    result = JsonCleaner.check_and_clean_json(test_str)
    assert result == '{key: "value"}'


def test_clean_newline_spaces_json():
    test_str = r'{key: "value"\n    \n}'
    result = JsonCleaner.check_and_clean_json(test_str)
    assert result == '{key: "value"}'

def test_has_newline_in_string():
    test_str = r'{key: "value\n"\n    \n}'
    result = JsonCleaner.check_and_clean_json(test_str)
    assert result == '{key: "value"}'
