from sqlalchemy import Integer, Column
from sqlalchemy.orm import sessionmaker

from superagi.models.agent import Agent
from superagi.models.base_model import DBBaseModel
from superagi.models.db import connect_db

engine = connect_db()
Session = sessionmaker(bind=engine)


class ClusterAgent(DBBaseModel):
    """
    Represents a cluster agent entity.

    Attributes:
        id (int): The unique identifier of the cluster agent.
        cluster_id (int): The identifier of the associated cluster.
        agent_id (int): The identifier of the associated agent.
    """

    __tablename__ = 'cluster_agents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_id = Column(Integer)
    agent_id = Column(Integer)

    def __repr__(self):
        """
        Returns a string representation of the Cluster Agent object.

        Returns:
            str: String representation of the Cluster Agent.

        """
        return f"ClusterAgent(id={self.id}, cluster_id={self.cluster_id}, agent_id={self.agent_id})"

    @classmethod
    def get_cluster_agents_by_cluster_id(cls, cluster_id: int):
        """
        Fetches the cluster agents for the given cluster id.

        Args:
            cluster_id (int): The identifier of the cluster.

        Returns:
            list: List of cluster agents.
        """
        session = Session()
        cluster_agents = session.query(cls).filter(cls.cluster_id == cluster_id).all()
        agents = []
        for cluster_agent in cluster_agents:
            print("CHECK IT OUT", cluster_agent)
            agent = session.query(Agent).filter(Agent.id == cluster_agent.agent_id).first()
            agents.append(agent)
        session.close()
        return agents

    @staticmethod
    def create_cluster_agents(cluster_id: int, agent_ids: [int]):
        """
        Creates the cluster agents for the given cluster id.

        Args:
            cluster_id (int): The identifier of the cluster.
            agent_ids (list): The list of agent ids.
        """

        session = Session()
        for agent_id in agent_ids:
            cluster_agent = ClusterAgent(cluster_id=cluster_id, agent_id=agent_id)
            session.add(cluster_agent)
        session.commit()
        session.close()
