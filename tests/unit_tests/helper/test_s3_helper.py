import json
import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import NoCredentialsError
from fastapi import HTTPException
from superagi.helper.s3_helper import S3Helper

@pytest.fixture()
def s3helper_object():
    return S3Helper()

def test__get_s3_client(s3helper_object):
    with patch('superagi.helper.s3_helper.get_config', return_value='test') as mock_get_config:
        s3_client = s3helper_object._S3Helper__get_s3_client()
        mock_get_config.assert_any_call('AWS_ACCESS_KEY_ID')
        mock_get_config.assert_any_call('AWS_SECRET_ACCESS_KEY')

@pytest.mark.parametrize('have_creds, raises', [(True, False), (False, True)])
def test_upload_file(s3helper_object, have_creds, raises):
    s3helper_object.s3.upload_fileobj = MagicMock()
    s3helper_object.s3.upload_fileobj.side_effect = NoCredentialsError() if not have_creds else None

    if raises:
        with pytest.raises(HTTPException):
            s3helper_object.upload_file('file', 'path')
    else:
        s3helper_object.upload_file('file', 'path')

@pytest.mark.parametrize('have_creds, raises', [(True, False), (False, True)])
def test_get_json_file(s3helper_object, have_creds, raises):
    
    # Mock 'get_object' method from s3 client
    s3helper_object.s3.get_object = MagicMock() 

    # Mocked JSON contents with their 'Body' key as per real response
    mock_json_file = { 'Body': MagicMock() }
    mock_json_file['Body'].read = MagicMock(return_value=bytes(json.dumps("content_of_json"), 'utf-8'))

    # Case when we do have credentials but 'get_object' raises an error
    if not raises:
        s3helper_object.s3.get_object.return_value = mock_json_file
    else:
        s3helper_object.s3.get_object.side_effect = NoCredentialsError() 

    # Mocking a path to the file
    mock_path = "mock_path"

    if raises:
        with pytest.raises(HTTPException):
            s3helper_object.get_json_file(mock_path)
    else:
        content = s3helper_object.get_json_file(mock_path)

        # Assert that 'get_object' was called with our mocked path
        s3helper_object.s3.get_object.assert_called_with(Bucket=s3helper_object.bucket_name, Key=mock_path) 

        assert content == "content_of_json"  # Assert we got our mocked JSON content back

def test_check_file_exists_in_s3(s3helper_object):
    s3helper_object.s3.list_objects_v2 = MagicMock(return_value={})
    assert s3helper_object.check_file_exists_in_s3('path') == False

    s3helper_object.s3.list_objects_v2 = MagicMock(return_value={'Contents':[]})
    assert s3helper_object.check_file_exists_in_s3('path') == True

@pytest.mark.parametrize('http_status, expected_result, raises', [(200, 'file_content', False), (500, None, True)])
def test_read_from_s3(s3helper_object, http_status, expected_result, raises):
    s3helper_object.s3.get_object = MagicMock(
        return_value={'ResponseMetadata': {'HTTPStatusCode': http_status},
                      'Body': MagicMock(read=lambda: bytes(expected_result, 'utf-8'))}
    )

    if raises:
        with pytest.raises(Exception):
            s3helper_object.read_from_s3('path')
    else:
        assert s3helper_object.read_from_s3('path') == expected_result

@pytest.mark.parametrize('http_status, expected_result, raises',
                         [(200, b'file_content', False),
                          (500, None, True)])
def test_read_binary_from_s3(s3helper_object, http_status, expected_result, raises):
    s3helper_object.s3.get_object = MagicMock(
        return_value={'ResponseMetadata': {'HTTPStatusCode': http_status},
                      'Body': MagicMock(read=lambda: (expected_result))}
    )

    if raises:
        with pytest.raises(Exception):
            s3helper_object.read_binary_from_s3('path')
    else:
        assert s3helper_object.read_binary_from_s3('path') == expected_result

def test_delete_file_success(s3helper_object):
    s3helper_object.s3.delete_object = MagicMock()
    try:
        s3helper_object.delete_file('path')
    except:
        pytest.fail("Unexpected Exception !")

def test_delete_file_fail(s3helper_object):
    s3helper_object.s3.delete_object = MagicMock(side_effect=Exception())
    with pytest.raises(HTTPException):
        s3helper_object.delete_file('path')


def test_list_files_from_s3(s3helper_object):
    s3helper_object.s3.list_objects_v2 = MagicMock(return_value={
        'Contents': [{'Key': 'path/to/file1.txt'}, {'Key': 'path/to/file2.jpg'}]
    })

    file_list = s3helper_object.list_files_from_s3('path/to/')

    assert len(file_list) == 2
    assert 'path/to/file1.txt' in file_list
    assert 'path/to/file2.jpg' in file_list


def test_list_files_from_s3_no_contents(s3helper_object):
    s3helper_object.s3.list_objects_v2 = MagicMock(return_value={})

    with pytest.raises(Exception):
        s3helper_object.list_files_from_s3('path/to/')


def test_list_files_from_s3_raises_exception(s3helper_object):
    s3helper_object.s3.list_objects_v2 = MagicMock(side_effect=Exception("An error occurred"))

    with pytest.raises(Exception):
        s3helper_object.list_files_from_s3('path/to/')
