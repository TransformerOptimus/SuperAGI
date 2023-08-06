import unittest
from unittest.mock import MagicMock, call
from superagi.models.agent_config import AgentConfiguration
from superagi.controllers.types.agent_execution_config import AgentRunIn

class TestAgentConfigurationsUpdate(unittest.TestCase):

    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_session.query().filter().first.return_value = None

        self.added_configurations = []
        self.mock_session.add.side_effect = lambda config: self.added_configurations.append(config)

    def test_update_toolkits_config(self):
        updated_details = AgentRunIn(agent_type="test", constraints=["c1", "c2"], toolkits=[1, 2], tools=[1, 2, 3], exit="exit", iteration_interval=1, model="test", permission_type="p", LTM_DB="LTM", max_iterations=100)

        AgentConfiguration.update_agent_configurations_table(self.mock_session, 1, updated_details)

        added_config = self.added_configurations[0]

        self.assertEqual(added_config.agent_id, 1)
        self.assertEqual(added_config.key, 'toolkits')
        self.assertEqual(added_config.value, [1, 2])
        self.assertEqual(self.added_configurations[1].agent_id, 1)
        self.assertEqual(self.added_configurations[1].key, 'knowledge')
        self.assertEqual(self.added_configurations[1].value, None)
        self.mock_session.commit.assert_called_once()
