import pytest
from superagi.models.events import Event
from superagi.apm.analytics_helper import AnalyticsHelper
from unittest.mock import MagicMock, Mock


def test_fetch_agent_data(mocker):
    # Mock session.query
    mocked_query = mocker.patch('sqlalchemy.orm.Session.query')

    mocked_query.return_value.all.return_value = [
        MagicMock(agents=1),
        MagicMock(agents=2)
    ]

    # Mock the return values of subqueries
    mocked_query.return_value.filter_by.return_value.subquery.return_value.c = MagicMock(agent_id='agent_id',
                                                                                         agent_name='agent_name',
                                                                                         model='model')
    mocked_query.return_value.filter.return_value.group_by.return_value.subquery.return_value.c = MagicMock(
        agent_id='agent_id', total_tokens=10, total_calls=2, runs_completed=1)
    mocked_query.return_value.filter_by.return_value.group_by.return_value.subquery.return_value.c = MagicMock(
        agent_id='agent_id', tools_used=['tool1', 'tool2'])
    mocked_query.return_value.join.return_value.group_by.return_value.subquery.return_value.c = MagicMock(
        agent_id='agent_id', avg_run_time=1000)

    # Mock the return values of final query
    mocked_query.return_value.outerjoin.return_value.outerjoin.return_value.outerjoin.return_value.all.return_value = [
        MagicMock(agent_id='agent_id', agent_name='agent_name', model='model', total_tokens=10, total_calls=2,
                  runs_completed=1, tools_used=['tool1', 'tool2'], avg_run_time=1000)
    ]

    session = Mock()
    org_id = 1
    analytics_helper = AnalyticsHelper(session, org_id)

    agent_data = analytics_helper.fetch_agent_data()

    # Check if the function returns the expected results
    assert agent_data['agent_details'][0]['name'] == 'agent_name'
    assert agent_data['agent_details'][0]['agent_id'] == 'agent_id'
    assert agent_data['agent_details'][0]['runs_completed'] == 1
    assert agent_data['agent_details'][0]['total_calls'] == 2
    assert agent_data['agent_details'][0]['total_tokens'] == 10
    assert agent_data['agent_details'][0]['tools_used'] == ['tool1', 'tool2']
    assert agent_data['agent_details'][0]['model_name'] == 'model'
    assert agent_data['agent_details'][0]['avg_run_time'] == 1000
