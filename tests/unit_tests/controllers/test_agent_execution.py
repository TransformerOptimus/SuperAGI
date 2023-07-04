# from unittest.mock import patch
#
# import pytest
# from fastapi.testclient import TestClient
#
# from main import app
# from superagi.models.agent_execution_config import AgentExecutionConfiguration
#
# client = TestClient(app)
#
#
# @pytest.fixture
# def mocks():
#     # Mock tool kit data for testing
#     mock_agent_execution = Age(status='RUNNING', last_execution_time=datetime.now(),
#                                      agent_id=self.agent_execution.agent_id, name=self.agent_execution.name,
#                                      num_of_calls=0, num_of_tokens=0, current_step_id=1)
#
# def test_create_agent_execution_success(mocks):
#     # Mocked database response
#     # mock_agent = MagicMock()
#     # mock_agent.agent_workflow_id = 1
#     # mock_db.session.query.return_value.get.return_value = mock_agent
#     # mock_db.session.query.return_value.filter.return_value.first.return_value = self.agent_execution
#     # Mocked agent_execution object
#     mock_agent_execution = MagicMock(status='RUNNING', last_execution_time=datetime.now(),
#                                      agent_id=self.agent_execution.agent_id, name=self.agent_execution.name,
#                                      num_of_calls=0, num_of_tokens=0, current_step_id=1)
#
#     with client:
#         response = client.post("/agentexecutions/add", json=self.agent_execution.dict())
#
#     assert response.status_code == 201
#     assert response.json() == mock_agent_execution
#
# @patch('main.check_auth')
# @patch('main.db')
# def test_create_agent_execution_not_found(mocks):
#     mock_db.session.query.return_value.get.return_value = None
#
#     with client:
#         response = client.post("/agentexecutions/add", json=self.agent_execution.dict())
#
#     assert response.status_code == 404
#     assert response.json() == {"detail": "Agent not found"}