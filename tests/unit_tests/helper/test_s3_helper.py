import pytest
import boto3
import json
from moto import mock_s3
from superagi.config.config import get_config
from superagi.helper.s3_helper import S3Helper

@mock_s3
class TestS3Helper:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_bucket = 'test_bucket'
        self.mock_s3 = boto3.client('s3')
        self.mock_s3.create_bucket(Bucket=self.mock_bucket)
        self.s3_helper = S3Helper()
        self.s3_helper.bucket_name = self.mock_bucket

    def test_upload_file(self):
        f = open('test.txt', 'w+')
        f.write('Hello, world!')
        f.close()

        with open('test.txt', 'rb') as f:
            self.s3_helper.upload_file(f, 'test.txt')

        response = self.mock_s3.list_objects(Bucket=self.mock_bucket)

        assert 'Contents' in response
        assert response['Contents'][0]['Key'] == 'test.txt'

    def test_get_json_file(self):
        json_data = {
            'name': 'test',
            'language': 'Python'
        }

        self.mock_s3.put_object(Bucket=self.mock_bucket, Key='test.json', Body=json.dumps(json_data))

        response = self.s3_helper.get_json_file('test.json')

        assert response == json_data