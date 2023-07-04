import unittest
from unittest.mock import MagicMock, patch
from superagi.models.agent_execution_config import AgentExecutionConfiguration


class TestAgentExecutionConfiguration(unittest.TestCase):

    def setUp(self):
        self.session = MagicMock()
        self.execution = MagicMock()
        self.execution.id = 1

    def test_add_or_update_agent_execution_config(self):
        test_config = {
            "goal": "test_goal",
            "instruction": "test_instruction"
        }

        with patch.object(AgentExecutionConfiguration, "__init__", return_value=None):
            with patch.object(self.session, "add"):
                with patch.object(self.session, "commit"):
                    AgentExecutionConfiguration.add_or_update_agent_execution_config(self.session, self.execution,
                                                                                     test_config)

        # additional assertions to validate behaviour can be added here

    def test_fetch_configuration(self):
        test_db_response = [MagicMock(key="goal", value="test_goal"),
                            MagicMock(key="instruction", value="test_instruction")]

        self.session.query.return_value.filter_by.return_value.all.return_value = test_db_response

        result = AgentExecutionConfiguration.fetch_configuration(self.session, self.execution)

        expected_result = {"goal": ["test_goal"], "instruction": ["test_instruction"]}
        self.assertDictEqual(result, expected_result)


    def test_eval_agent_config(self):
        key = "goal"
        value = "['test_goal']"

        result = AgentExecutionConfiguration.eval_agent_config(key, value)

        self.assertEqual(result, ["test_goal"])
