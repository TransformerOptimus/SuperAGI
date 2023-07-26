import unittest
from datetime import datetime

from superagi.helper.feed_parser import parse_feed
from superagi.models.agent_execution_feed import AgentExecutionFeed


class TestParseFeed(unittest.TestCase):

    def test_parse_feed_system(self):
        current_time = datetime.now()

        # Create a sample AgentExecutionFeed object with a system role
        sample_feed = AgentExecutionFeed(id=2, agent_execution_id=100, agent_id=200, role="assistant",
                                         feed='System message',
                                         updated_at=current_time)

        # Call the parse_feed function with the sample_feed object
        result = parse_feed(sample_feed)

        # In this test case, we only ensure that the parse_feed function doesn't modify the given feed
        self.assertEqual(result, sample_feed, "Incorrect output from parse_feed function for system role")
