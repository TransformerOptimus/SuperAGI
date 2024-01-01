import pytest
from unittest.mock import MagicMock
from superagi.models.resource import Resource


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.query.return_value.filter.return_value.all.return_value = None
    return session


@pytest.mark.parametrize("name, storage_type, path, size, type, channel, agent_id, agent_execution_id",
                         [("example_resource", "FILE", "/path/to/resource", 100, "application/pdf", "INPUT", 1, 1)])
def test_create_resource(mock_session, name, storage_type, path, size, type, channel, agent_id, agent_execution_id):
    resource = Resource(name=name,storage_type=storage_type,path=path,size=size,type=type,channel=channel,
                        agent_id=agent_id,agent_execution_id=agent_execution_id)
    # Act
    mock_session.add(resource)

    # Assert
    mock_session.add.assert_called_once_with(resource)


@pytest.mark.parametrize("run_ids", [[1, 2, 3]])
def test_find_by_run_ids(mock_session, run_ids):
    # Arrange
    expected_resources = [MagicMock(), MagicMock(), MagicMock()]
    mock_session.query.return_value.filter.return_value.all.return_value = expected_resources

    # Act
    result = Resource.find_by_run_ids(mock_session, run_ids)

    # Assert
    mock_session.query.assert_called_once_with(Resource)
    mock_session.query.return_value.filter.assert_called_once()
    assert result == expected_resources


@pytest.mark.parametrize("file_name, agent_id, agent_execution_id", [("example_resource", 1, 1)])
def test_delete_resource(mock_session, file_name, agent_id, agent_execution_id):
    # Arrange
    mock_session.query.return_value.filter.return_value.delete.return_value = 1

    # Act
    deleted = Resource.delete_resource(mock_session, file_name, agent_id, agent_execution_id)

    # Assert
    mock_session.query.assert_called_once_with(Resource)
    mock_session.query.return_value.filter.assert_called_once()
    mock_session.commit.assert_called_once()
    assert deleted == 1
