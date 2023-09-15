from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import app
from superagi.models.user import User

client = TestClient(app)

# Define a fixture for an authenticated user
@pytest.fixture
def authenticated_user():
    # Create a mock user object with necessary attributes
    user = User()

    # Set user attributes
    user.id = 1  # User ID
    user.username = "testuser"  # User's username
    user.email = "super6@agi.com"  # User's email
    user.first_login_source = None  # User's first login source
    user.token = "mock-jwt-token"

    return user

# Test case for updating first login source when it's not set
def test_update_first_login_source(authenticated_user):
    with patch('superagi.helper.auth.db') as mock_auth_db:
        source = "github"  # Specify the source you want to set

        mock_auth_db.session.query.return_value.filter.return_value.first.return_value = authenticated_user
        response = client.post(f"users/first_login_source/{source}", headers={"Authorization": f"Bearer {authenticated_user.token}"})

        # Verify the HTTP response
        assert response.status_code == 200
        assert "first_login_source" in response.json()  # Check if the "first_login_source" field is in the response
        assert response.json()["first_login_source"] == "github"  # Check if the "source" field equals "github"