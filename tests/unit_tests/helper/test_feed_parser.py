import unittest
from datetime import datetime
from superagi.helper.feed_parser import parse_feed
from superagi.models.agent_execution_feed import AgentExecutionFeed
class TestParseFeed(unittest.TestCase):
    def test_parse_feed_system(self):
        current_time = datetime.now()
        sample_feed = AgentExecutionFeed(
            id=2, agent_execution_id=100, agent_id=200, role="user",
            feed='System message', updated_at=current_time
        )

        result = parse_feed(sample_feed)
        
        self.assertEqual(result['feed'], sample_feed.feed, "Incorrect output from parse_feed function for system role")
        self.assertEqual(result['role'], sample_feed.role, "Incorrect output from parse_feed function for system role")