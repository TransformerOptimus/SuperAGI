import base64
import unittest
from unittest.mock import patch, MagicMock

from superagi.helper.github_helper import GithubHelper

class TestGithubHelper(unittest.TestCase):
    @patch('requests.get')
    def test_check_repository_visibility(self, mock_get):
        # Create response mock
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'private': False}
        mock_get.return_value = mock_resp

        gh = GithubHelper('access_token', 'username')
        visibility = gh.check_repository_visibility('owner', 'repo')

        self.assertEqual(visibility, False)
        mock_get.assert_called_once_with(
            "https://api.github.com/repos/owner/repo",
            headers={"Authorization": "Token access_token", "Accept": "application/vnd.github.v3+json"}
        )

    @patch('requests.get')
    def test_get_file_path(self, mock_get):
        gh = GithubHelper('access_token', 'username')
        path = gh.get_file_path('test.txt', 'dir')
        self.assertEqual(path, 'dir/test.txt')


    @patch('requests.get')
    def test_search_repo(self, mock_get):
        # Create response mock
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = 'data'
        mock_get.return_value = mock_resp

        gh = GithubHelper('access_token', 'username')
        data = gh.search_repo('owner', 'repo', 'test.txt', '')

        self.assertEqual(data, 'data')
        mock_get.assert_called_once_with(
            'https://api.github.com/repos/owner/repo/contents/test.txt',
            headers={"Authorization": "token access_token", "Content-Type": "application/vnd.github+json"}
        )

    @patch('requests.get')
    @patch('requests.patch')
    def test_sync_branch(self, mock_patch, mock_get):
        # Create response mocks
        mock_get_resp = MagicMock()
        mock_get_resp.json.return_value = {'commit': {'sha': 'sha'}}
        mock_get.return_value = mock_get_resp
        mock_patch_resp = MagicMock()
        mock_patch_resp.status_code = 200
        mock_patch.return_value = mock_patch_resp

        gh = GithubHelper('access_token', 'username')
        gh.sync_branch('owner', 'repo', 'base', 'head', {'header': 'value'})

        mock_get.assert_called_once_with(
            'https://api.github.com/repos/owner/repo/branches/base',
            headers={'header': 'value'}
        )
        mock_patch.assert_called_once_with(
            'https://api.github.com/repos/username/repo/git/refs/heads/head',
            json={'sha': 'sha', 'force': True},
            headers={'header': 'value'}
        )

    @patch('requests.get')
    @patch('requests.post')
    def test_create_branch(self, mock_post, mock_get):
        # Create response mocks
        mock_get_resp = MagicMock()
        mock_get_resp.json.return_value = {'object': {'sha': 'sha'}}
        mock_get.return_value = mock_get_resp
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 201
        mock_post.return_value = mock_post_resp

        gh = GithubHelper('access_token', 'username')
        status_code = gh.create_branch('repo', 'base', 'head', {'header': 'value'})

        self.assertEqual(status_code, 201)
        mock_get.assert_called_once_with(
            'https://api.github.com/repos/username/repo/git/refs/heads/base',
            headers={'header': 'value'}
        )
        mock_post.assert_called_once_with(
            'https://api.github.com/repos/username/repo/git/refs',
            json={'ref': 'refs/heads/head', 'sha': 'sha'},
            headers={'header': 'value'}
        )

    @patch('requests.post')
    def test_make_fork(self, mock_post):
        # Create response mock
        mock_resp = MagicMock()
        mock_resp.status_code = 202
        mock_post.return_value = mock_resp

        gh = GithubHelper('access_token', 'username')
        with patch.object(GithubHelper, 'sync_branch') as mock_sync:
            status_code = gh.make_fork('owner', 'repo', 'base', {'header': 'value'})

        self.assertEqual(status_code, 202)
        mock_post.assert_called_once_with(
            'https://api.github.com/repos/owner/repo/forks',
            headers={'header': 'value'}
        )
        mock_sync.assert_called_once_with('owner', 'repo', 'base', 'base', {'header': 'value'})

    @patch('requests.delete')
    def test_delete_file(self, mock_delete):
        # Create response mock
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_delete.return_value = mock_resp

        gh = GithubHelper('access_token', 'username')
        with patch.object(GithubHelper, 'get_sha', return_value='sha') as mock_sha:
            status_code = gh.delete_file('repo', 'test.txt', 'path', 'message', 'head', {'header': 'value'})

        self.assertEqual(status_code, 200)
        mock_sha.assert_called_once_with('username', 'repo', 'test.txt', 'path')
        mock_delete.assert_called_once_with(
            'https://api.github.com/repos/username/repo/contents/path/test.txt',
            json={'message': 'message', 'sha': 'sha', 'branch': 'head'},
            headers={'header': 'value'}
        )

    @patch('requests.post')
    def test_create_pull_request(self, mock_post):
        # Create response mock
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_post.return_value = mock_resp

        gh = GithubHelper('access_token', 'username')
        status_code = gh.create_pull_request('owner', 'repo', 'head', 'base', {'header': 'value'})

        self.assertEqual(status_code, 201)
        mock_post.assert_called_once_with(
            'https://api.github.com/repos/owner/repo/pulls',
            json={
                'title': 'Pull request by username',
                'body': 'Please review and merge this change.',
                'head': 'username:head',
                'head_repo': 'repo',
                'base': 'base'
            },
            headers={'header': 'value'}
        )

    # ... more tests for other methods

if __name__ == '__main__':
    unittest.main()