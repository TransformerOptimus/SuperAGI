from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_feed import AgentExecutionFeed

class ErrorHandler:

    def handle_openai_errors(session, agent_id, agent_execution_id, error_message):
        execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
        agent_feed = AgentExecutionFeed(agent_execution_id=agent_execution_id, agent_id=agent_id, role="system", feed="", error_message=error_message, feed_group_id=execution.current_feed_group_id)
        session.add(agent_feed)
        session.commit()