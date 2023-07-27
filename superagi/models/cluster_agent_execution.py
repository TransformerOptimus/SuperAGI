from sqlalchemy import Integer, Column

from superagi.models.base_model import DBBaseModel


class ClusterAgentExecution(DBBaseModel):


    """
    Agent Executions which runs part of cluster execution.

    Attributes:
        id (int): The unique identifier of the agent execution.
        agent_execution_id (int): The unique identifier of the agent execution.
        cluster_execution_id (int): The unique identifier of the cluster execution.
    """

    __tablename__ = 'cluster_agent_executions'

    id = Column(Integer, primary_key=True)
    agent_execution_id = Column(Integer)
    cluster_execution_id = Column(Integer)


    def __repr__(self):
        """
        Returns a string representation of the AgentExecution object.

        Returns:
            str: String representation of the AgentExecution.
        """

        return f"AgentExecution(id={self.id}, agent_execution_id='{self.agent_execution_id}', " \
               f"cluster_execution_id='{self.cluster_execution_id}')"


    @classmethod
    def get_cluster_execution_id_by_agent_execution_id(cls, session, agent_execution_id):
        """
        Check if cluster agent execution exists

        Args:
            agent_execution_id (int): The unique identifier of the agent execution.
            cluster_execution_id (int): The unique identifier of the cluster execution.

        Returns:
            bool: True if cluster agent execution exists, False otherwise.
        """

        cluster_agent_execution = session.query(cls).filter_by(agent_execution_id=agent_execution_id).first()
        if cluster_agent_execution:
            return cluster_agent_execution.cluster_execution_id
        else:
            return None