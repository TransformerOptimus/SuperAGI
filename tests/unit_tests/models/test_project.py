from unittest.mock import create_autospec

from sqlalchemy.orm import Session
from superagi.models.project import Project

def test_find_by_org_id():
    # Create a mock session
    session = create_autospec(Session)

    # Create a sample org ID
    org_id = 123

    # Create a mock project object to be returned by the session query
    mock_project = Project(id=1, name="Test Project", organisation_id=org_id, description="Project for testing")

    # Configure the session query to return the mock project
    session.query.return_value.filter.return_value.first.return_value = mock_project

    # Call the method under test
    project = Project.find_by_org_id(session, org_id)

    # Assert that the returned project object matches the mock project
    assert project == mock_project

def test_find_by_id():
    # Create a mock session
    session = create_autospec(Session)

    # Create a sample project ID
    project_id = 123

    # Create a mock project object to be returned by the session query
    mock_project = Project(id=project_id, name="Test Project", organisation_id=1, description="Project for testing")

    # Configure the session query to return the mock project
    session.query.return_value.filter.return_value.first.return_value = mock_project

    # Call the method under test
    project = Project.find_by_id(session, project_id)

    # Assert that the returned project object matches the mock project
    assert project == mock_project